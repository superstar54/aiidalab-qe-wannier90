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
        wannier90_bands['plot_settings'] = {'dash': 'dash'}
        model = BandsPdosModel(bands = pw_bands,
                               external_bands = {'wannier90_bands': wannier90_bands}
                            )

        # Create and render the bands/PDOS widget
        bands_widget = BandsPdosWidget(model=model)
        bands_widget.render()

        # Wannier90 outputs summary (merged with bands distance)
        wannier90_outputs = self._model.wannier90_outputs
        bands_distance = self._model.bands_distance

        wannier90_outputs_parameters = ipw.HTML(
            f"""
            <div style="margin-top:10px; padding:10px; border:1px solid #ddd; border-radius:5px;">
                <table style="width:100%; border-collapse:collapse;">
                    <tr>
                        <td><b>Number of WFs:</b> {wannier90_outputs['number_wfs']}</td>
                        <td><b>Ω<sub>D</sub>:</b> {wannier90_outputs['Omega_D']}</td>
                        <td><b>Ω<sub>I</sub>:</b> {wannier90_outputs['Omega_I']}</td>
                        <td><b>Ω<sub>OD</sub>:</b> {wannier90_outputs['Omega_OD']}</td>
                    </tr>
                    <tr>
                        <td colspan="4"><b>Band Distance:</b> {bands_distance} eV (Good if ≤ 0.03 eV)</td>
                    </tr>
                </table>
            </div>
            """
        )

        # Omega convergence plot
        omega_is = self._model.omega_is
        fig = px.line(
            x=range(len(omega_is)), y=omega_is,
            title='Convergence of Omega_I vs Number of Iterations'
        )
        fig.update_yaxes(title='Omega_I')
        fig.update_xaxes(title='Number of iterations')
        self.plot_omega_is = go.FigureWidget(fig)
        #
        omega_tots = self._model.omega_tots
        fig = px.line(
            x=range(len(omega_tots)), y=omega_tots,
            title='Convergence of Omega_TOT vs Number of Iterations'
        )
        fig.update_yaxes(title='Omega_TOT')
        fig.update_xaxes(title='Number of iterations')
        self.plot_omega_tots = go.FigureWidget(fig)

        # structure
        self.structure_viewer = WeasWidget()
        atoms = self._model.structure.get_ase()
        self.structure_viewer.from_ase(atoms)
        # isosurface
        self.all_isosurface = self._model.get_isosurface()

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
        table_section = ipw.VBox([
            ipw.HTML('<h3>Wannier centers/spreads</h3>'),
            self.table
        ], layout=ipw.Layout(margin='10px 0'))




        # Arrange components in the panel
        self.children = [
            ipw.VBox([
                ipw.HTML('<h2>Bands structure</h2>'),
                bands_widget,
            ]),
            ipw.VBox([
                ipw.HTML('<h2>Wannier90 summary</h2>'),
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
        isosurface = self.all_isosurface[key]
        data = []
        if 'isovalue' in isosurface:
            for item in ['positive', 'negative']:
                vertices = isosurface[item]['vertices']
                vertices = [item for sublist in vertices for item in sublist]
                faces = isosurface[item]['faces']
                faces = [item for sublist in faces for item in sublist]
                data.append({
                        'name': item,
                        'color': ISOSURFACE_COLOR[item],
                        'material': 'Standard',
                        'position': [0, 0.0, 0.0],
                        'vertices': vertices,
                        'faces': faces,
                    })
        self.structure_viewer.any_mesh.settings = data
