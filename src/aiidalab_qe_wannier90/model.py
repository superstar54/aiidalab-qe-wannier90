import traitlets as tl
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel


class ConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = 'Wannier functions'
    identifier = 'wannier90'

    dependencies = [
        'input_structure',
        'workchain.protocol',
        'workchain.electronic_type',
    ]
    # by default: exclude semicore orbitals in both methods, since these low-energy states correspond
    # to almost flat bands and do not play any role in the chemistry of the materials
    exclude_semicore = tl.Bool(allow_none=True, default_value=True)
    scan_pdwf_parameter = tl.Bool(allow_none=True, default_value=False)
    plot_wannier_functions = tl.Bool(allow_none=True, default_value=False)
    number_of_disproj_max = tl.Int(allow_none=True, default_value=15)
    number_of_disproj_min = tl.Int(allow_none=True, default_value=2)
    retrieve_hamiltonian = tl.Bool(allow_none=True, default_value=True)
    retrieve_matrices = tl.Bool(allow_none=True, default_value=False)
    projection_type = tl.Unicode(allow_none=True, default_value='atomic_projectors_qe')
    frozen_type = tl.Unicode(allow_none=True, default_value='fixed_plus_projectability')
    energy_window_input = tl.Float(allow_none=True, default_value=2.0)
    compute_fermi_surface = tl.Bool(allow_none=True, default_value=False)
    fermi_surface_kpoint_distance = tl.Float(allow_none=True, default_value=0.04)
    compute_dhva_frequencies = tl.Bool(allow_none=True, default_value=False)
    # dHvA frequencies
    dhva_starting_phi = tl.Float(allow_none=True, default_value=0.0)
    dhva_starting_theta = tl.Float(allow_none=True, default_value=90.0)
    dhva_ending_phi = tl.Float(allow_none=True, default_value=90.0)
    dhva_ending_theta = tl.Float(allow_none=True, default_value=90.0)
    dhva_num_rotation = tl.Int(allow_none=True, default_value=90)

    protocol = tl.Unicode(allow_none=True)
    electronic_type = tl.Unicode(allow_none=True)

    def get_model_state(self):
        state = {
            'exclude_semicore': self.exclude_semicore,
            'plot_wannier_functions': self.plot_wannier_functions,
            'retrieve_hamiltonian': self.retrieve_hamiltonian,
            'retrieve_matrices': self.retrieve_matrices,
            'number_of_disproj_max': self.number_of_disproj_max,
            'number_of_disproj_min': self.number_of_disproj_min,
            'projection_type': self.projection_type,
            'frozen_type': self.frozen_type,
            'energy_window_input': self.energy_window_input,
            'compute_fermi_surface': self.compute_fermi_surface,
            'scan_pdwf_parameter': self.scan_pdwf_parameter,
        }
        if self.compute_fermi_surface:
            state |= {
                'fermi_surface_kpoint_distance': self.fermi_surface_kpoint_distance,
                'compute_dhva_frequencies': self.compute_dhva_frequencies,
            }
            if self.compute_dhva_frequencies:
                state |= {
                    'dHvA_frequencies_parameters': {
                        'starting_phi': self.dhva_starting_phi,
                        'starting_theta': self.dhva_starting_theta,
                        'ending_phi': self.dhva_ending_phi,
                        'ending_theta': self.dhva_ending_theta,
                        'num_rotation': self.dhva_num_rotation,
                    },
                }
        return state

    def set_model_state(self, parameters: dict):
        self.exclude_semicore = parameters.get('exclude_semicore', True)
        self.plot_wannier_functions = parameters.get('plot_wannier_functions', False)
        self.number_of_disproj_max = parameters.get('number_of_disproj_max', 15)
        self.number_of_disproj_min = parameters.get('number_of_disproj_min', 2)
        self.compute_dhva_frequencies = parameters.get('compute_dhva_frequencies', False)
        self.dhva_ending_phi = parameters.get('dHvA_frequencies_parameters', {}).get('ending_phi', 90.0)
        self.dhva_ending_theta = parameters.get('dHvA_frequencies_parameters', {}).get('ending_theta', 90.0)
        self.dhva_starting_phi = parameters.get('dHvA_frequencies_parameters', {}).get('starting_phi', 0.0)
        self.dhva_starting_theta = parameters.get('dHvA_frequencies_parameters', {}).get('starting_theta', 90.0)
        self.dhva_num_rotation = parameters.get('dHvA_frequencies_parameters', {}).get('num_rotation', 90)
        self.scan_pdwf_parameter = parameters.get('scan_pdwf_parameter', False)
