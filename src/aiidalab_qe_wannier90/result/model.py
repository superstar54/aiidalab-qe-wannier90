from aiidalab_qe.common.panel import ResultsModel
from aiida.common.extendeddicts import AttributeDict
import traitlets as tl
from aiida import orm
import time

class Wannier90ResultsModel(ResultsModel):
    title = 'Wannier functions'
    identifier = 'wannier90'
    structure = tl.Instance(orm.StructureData, allow_none=True)
    bands_distance = tl.Float(allow_none=True)
    wannier_centers_spreads = tl.Dict(allow_none=True)
    omega_is = tl.List(allow_none=True)
    omega_tots = tl.List(allow_none=True)
    im_re_ratio = tl.List(allow_none=True)
    wannier90_outputs = tl.Dict(allow_none=True)

    _this_process_label = 'QeAppWannier90BandsWorkChain'

    def fetch_result(self):
        root = self.fetch_process_node()
        self.structure = root.outputs.wannier90.pw_bands.primitive_structure
        self.bands_distance = root.outputs.wannier90.wannier90_bands.bands_distance.value
        data = root.outputs.wannier90.wannier90_bands.wannier90_optimal.output_parameters.get_dict()
        self.wannier90_outputs = {key: data[key] for key in ['number_wfs', 'Omega_D', 'Omega_I', 'Omega_OD']}
        # Wannier centers/spreads
        self.wannier_centers_spreads = self.get_wannier_centers_spreads(root)
        self.omega_is, self.omega_tots = self.get_omega(root)

    def get_omega(self, root):
        omega_is = []
        omega_tots = []
        with root.outputs.wannier90.wannier90_bands.wannier90_optimal.retrieved.open('aiida.wout') as f:
            lines = f.readlines()
            for line in lines:
                if '  <-- DIS' in line:
                    omega_i = float(line.split()[2])
                    omega_is.append(omega_i)
                if '<-- SPRD' in line:
                    omega_tot = float(line.split('O_TOT=')[1].split('<-- SPRD')[0])
                    omega_tots.append(omega_tot)
        return omega_is, omega_tots

    def get_wannier_centers_spreads(self, node):
        outputs = node.outputs.wannier90.wannier90_bands.wannier90_optimal.output_parameters.get_dict()
        columns = [
            {'field': 'id', 'headerName': 'WF', 'editable': False},
            {'field': 'spreads_initial', 'headerName': 'Initial spread (first iteration) (Å2)', 'editable': False, 'width': 130,},
            {'field': 'spreads_final', 'headerName': 'Final spread (Å2)', 'editable': False, 'width': 130,},
            {'field': 'centers_final', 'headerName': 'Centers final (Å)', 'editable': False, 'width': 180,},
            {'field': 'centers_initial', 'headerName': 'Centers initial (Å)', 'editable': False, 'width': 180,},
        ]
        if 'wannier90_plot' in node.outputs.wannier90.wannier90_bands:
            plot_parameters = node.outputs.wannier90.wannier90_bands.wannier90_plot.output_parameters.get_dict()
            columns.append({'field': 'im_re_ratio', 'headerName': 'Im_re_ratio', 'editable': False})
        else:
            plot_parameters = None
        centers_spreads = {'columns': columns,
                           'data': []}
        for i in range(len(outputs['wannier_functions_initial'])):
            data = {
                'id': i + 1,
                'spreads_initial': round(outputs['wannier_functions_initial'][i]['wf_spreads'], 3),
                'spreads_final': round(outputs['wannier_functions_output'][i]['wf_spreads'], 3),
                'centers_initial': '[' + ', '.join(f'{x:.4f}' for x in outputs['wannier_functions_initial'][i]['wf_centres']) + ']',
                'centers_final': '[' + ', '.join(f'{x:.4f}' for x in outputs['wannier_functions_output'][i]['wf_centres']) + ']',
            }

            centers_spreads['data'].append(data)
            if plot_parameters:
                data['im_re_ratio'] = plot_parameters['wannier_functions_output'][i]['im_re_ratio']

        return centers_spreads

    def get_bands_node(self):
        outputs = self._get_child_outputs()
        pw_bands = outputs.pw_bands
        wannier90_bands = AttributeDict()
        for key in pw_bands.keys():
            wannier90_bands[key] = pw_bands[key]
        wannier90_bands['band_structure'] = outputs.wannier90_bands.band_structure
        return pw_bands, wannier90_bands

    def get_isosurface(self) -> dict:
        outputs = self._get_child_outputs()
        if 'generate_isosurface' not in outputs:
            return None
        atoms = outputs.generate_isosurface.atoms.value
        parameters = outputs.generate_isosurface.parameters.get_dict()
        mesh_data = outputs.generate_isosurface.mesh_data

        return {'atoms': atoms, 'parameters': parameters, 'mesh_data': mesh_data}
