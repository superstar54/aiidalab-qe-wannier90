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

    protocol = tl.Unicode(allow_none=True)

    def get_model_state(self):
        return {
            'exclude_semicore': self.exclude_semicore,
            'plot_wannier_functions': self.plot_wannier_functions,
        }

    def set_model_state(self, parameters: dict):
        self.exclude_semicore = parameters.get('exclude_semicore', True)
        self.plot_wannier_functions = parameters.get('plot_wannier_functions', False)
