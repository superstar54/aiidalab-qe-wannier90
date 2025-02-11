import traitlets as tl
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel


class ConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = 'Wannier90'
    identifier = 'wannier90'

    dependencies = [
        'input_structure',
        'workchain.protocol',
        'workchain.electronic_type',
    ]
    exclude_semicore = tl.Bool(allow_none=True, default_value=True)
    plot_wannier_functions = tl.Bool(allow_none=True, default_value=False)
    number_of_disproj_max = tl.Int(allow_none=True, default_value=15)
    number_of_disproj_min = tl.Int(allow_none=True, default_value=2)
    retrieve_hamiltonian = tl.Bool(allow_none=True, default_value=True)
    retrieve_matrices = tl.Bool(allow_none=True, default_value=False)
    projection_type = tl.Unicode(allow_none=True, default_value='atomic_projectors_qe')
    frozen_type = tl.Unicode(allow_none=True, default_value='fixed_plus_projectability')

    protocol = tl.Unicode(allow_none=True)
    electronic_type = tl.Unicode(allow_none=True)

    def get_model_state(self):
        return {
            'exclude_semicore': self.exclude_semicore,
            'plot_wannier_functions': self.plot_wannier_functions,
            'retrieve_hamiltonian': self.retrieve_hamiltonian,
            'retrieve_matrices': self.retrieve_matrices,
            'number_of_disproj_max': self.number_of_disproj_max,
            'number_of_disproj_min': self.number_of_disproj_min,
            'projection_type': self.projection_type,
            'frozen_type': self.frozen_type,
        }

    def set_model_state(self, parameters: dict):
        self.exclude_semicore = parameters.get('exclude_semicore', True)
        self.plot_wannier_functions = parameters.get('plot_wannier_functions', False)
        self.number_of_disproj_max = parameters.get('number_of_disproj_max', 15)
        self.number_of_disproj_min = parameters.get('number_of_disproj_min', 2)
