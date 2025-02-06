import traitlets as tl
from aiida_quantumespresso.workflows.pdos import PdosWorkChain
from aiidalab_qe.common.mixins import HasInputStructure
from aiidalab_qe.common.panel import ConfigurationSettingsModel


class ConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = 'Wannier90'
    identifier = 'wannier90'

    dependencies = [
        'input_structure',
        'workchain.protocol',
    ]
    exclude_semicore = tl.Bool(allow_none=True, default_value=True)
    plot_wannier_functions = tl.Bool(allow_none=True, default_value=False)
    number_of_disproj_max = tl.Int(allow_none=True, default_value=15)
    number_of_disproj_min = tl.Int(allow_none=True, default_value=2)
    compute_hamiltonian = tl.Bool(allow_none=True, default_value=True)
    projection_type = tl.Unicode(allow_none=True, default_value='atomic_projectors_qe')
    frozen_type = tl.Unicode(allow_none=True, default_value='fixed_plus_projectability')

    protocol = tl.Unicode(allow_none=True)

    def get_model_state(self):
        return {
            'exclude_semicore': self.exclude_semicore,
            'plot_wannier_functions': self.plot_wannier_functions,
            'compute_hamiltonian': self.compute_hamiltonian,
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
