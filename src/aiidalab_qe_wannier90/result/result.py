"""Wannier90 results view widgets"""

from aiidalab_qe.common.bands_pdos import BandsPdosModel, BandsPdosWidget
from aiidalab_qe.common.panel import ResultsPanel
import ipywidgets as ipw
from .model import Wannier90ResultsModel
from table_widget import TableWidget
import plotly.graph_objs as go
import plotly.express as px
from weas_widget import WeasWidget
import ast
import numpy as np

# Define a threshold for considering atoms "almost equally distant"
DISTANCE_THRESHOLD = 0.01

ISOSURFACE_COLOR = {
    'positive': [1.0, 1.0, 0.0, 0.8],
    'negative': [0.0, 1.0, 1.0, 0.8],
}

class Wannier90ResultsPanel(ResultsPanel[Wannier90ResultsModel]):

    def _render(self):
        """Render the Wannier90 results panel."""
        self._model.fetch_result()

        # Retrieve band structures
        pw_bands, wannier90_bands = self._model.get_bands_node()
        wannier90_bands['trace_settings'] = {'dash': 'dash',
                                             'shape': 'linear',
                                             'color': 'red'}
        model = BandsPdosModel(bands = pw_bands,
                               external_bands = {'Wannier-interpolated bands': wannier90_bands},
                               plot_settings = {'bands_trace_settings': {'name': 'DFT Bands'}},
                            )

        # Create and render the bands/PDOS widget
        bands_widget = BandsPdosWidget(model=model)
        bands_widget.render()

        # Wannier90 outputs summary (merged with bands distance)
        wannier90_outputs = self._model.wannier90_outputs
        bands_distance = self._model.bands_distance
        omega_tot = wannier90_outputs['Omega_D'] + wannier90_outputs['Omega_I'] + wannier90_outputs['Omega_OD']

        wannier90_outputs_parameters = ipw.HTML(
            f"""
            <div style="margin-top:10px; padding:15px;">
            <table style="width:60%; border-collapse:collapse; text-align:left; font-size:14px;">
                <tr>
                <td><b>Number of WFs:</b></td>
                <td>{wannier90_outputs['number_wfs']}</td>
                </tr>
                <tr>
                <td><b>Total spread Ω<sub>tot</sub>:</b></td>
                <td>{omega_tot:.3f} Å²</td>
                </tr>

                <tr>
                <td><b>Components of the spread:</b></td>
                <td>Ω<sub>D</sub>: {wannier90_outputs['Omega_D']:.3f} Å² &nbsp;&nbsp;
                    Ω<sub>I</sub>: {wannier90_outputs['Omega_I']:.3f} Å² &nbsp;&nbsp;
                    Ω<sub>OD</sub>: {wannier90_outputs['Omega_OD']:.3f} Å²
                </td>
                </tr>

                <tr>
                <td><b>Band Distance:</b></td>
                <td>{bands_distance * 1000:.3f} meV</td>
                </tr>
            </table>
            </div>
            """
        )


        # Omega convergence plot
        omega_is = self._model.omega_is
        fig = px.line(
            x=range(len(omega_is)), y=omega_is,
            title='Convergence of Ωᵢ'
        )
        fig.update_yaxes(title='Ωᵢ')
        fig.update_xaxes(title='Number of iterations')
        self.plot_omega_is = go.FigureWidget(fig)
        #
        omega_tots = self._model.omega_tots
        fig = px.line(
            x=range(len(omega_tots)), y=omega_tots,
            title='Convergence of Ωₜₒₜ'
        )
        fig.update_yaxes(title='Ωₜₒₜ')
        fig.update_xaxes(title='Number of iterations')
        self.plot_omega_tots = go.FigureWidget(fig)

        # structure
        self.structure_viewer = WeasWidget()
        atoms = self._model.structure.get_ase()
        self.structure_viewer.from_ase(atoms)
        self.structure_viewer.avr.model_style = 1
        self.structure_viewer.avr.color_type = 'VESTA'
        self.structure_viewer.avr.boundary = [[-0.05, 1.05], [-0.05, 1.05], [-0.05, 1.05]]
        # isosurface
        self.isosurface_data = self._model.get_isosurface()

        structure_viewer_section = ipw.VBox([
            ipw.HTML('<h3>Structure</h3>'),
            self.structure_viewer,
        ], layout=ipw.Layout(margin='10px 0'))

        # Wannier centers/spreads table
        self.table = TableWidget(style={'margin-top': '10px'})
        self.table.from_data(
            self._model.wannier_centers_spreads['data'],
            columns=self._model.wannier_centers_spreads['columns']
        )

        self.table.observe(self.on_single_row_select, 'selectedRowId')
        self.table_description = ipw.HTML('Click on a table row to visualize on the right the corresponding Wannier function in real space.')
        table_section = ipw.VBox([
            ipw.HTML('<h3>Wannier centers/spreads</h3>'),
            self.table_description,
            self.table
        ], layout=ipw.Layout(margin='10px 0'))




        # Arrange components in the panel
        self.children = [
            ipw.VBox([
                ipw.HTML('<h2>DFT and Wannier-interpolated electronic band structure</h2>'),
                bands_widget,
            ]),
            ipw.VBox([
                ipw.HTML('<h2>Wannierization details</h2>'),
                wannier90_outputs_parameters,
                ipw.HBox([self.plot_omega_is, self.plot_omega_tots]),
                ipw.HBox([structure_viewer_section, table_section]),
            ]),
        ]

    def on_single_row_select(self, change):
        id = change['new']
        center = [row['centers_final'] for row in self.table.data if row['id'] == id][0]
        center = ast.literal_eval(center)
        atoms = self._model.structure.get_ase()
        positions = atoms.get_positions()
        distances = np.linalg.norm(positions - center, axis=1)
        # Find minimum distance
        min_distance = np.min(distances)
        # Find all atoms that are within the threshold of the minimum distance
        indices = np.where(np.abs(distances - min_distance) < DISTANCE_THRESHOLD)[0]
        self.structure_viewer.avr.selected_atoms_indices = indices.tolist()
        key = f'aiida_{int(id):05d}'
        data = []
        if 'isovalue' in self.isosurface_data['parameters'][key]:
            for item in ['positive', 'negative']:
                vertices = self.isosurface_data['mesh_data'][f'{key}_{item}_vertices'].value.tolist()
                faces = self.isosurface_data['mesh_data'][f'{key}_{item}_faces'].value.tolist()
                data.append({
                        'name': item,
                        'color': ISOSURFACE_COLOR[item],
                        'material': 'Standard',
                        'position': [0, 0.0, 0.0],
                        'vertices': vertices,
                        'faces': faces,
                    })
        self.structure_viewer.any_mesh.settings = data
