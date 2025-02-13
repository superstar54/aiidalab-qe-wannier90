from aiidalab_qe.common.panel import PluginOutline

from .model import ConfigurationSettingsModel
from .resources import ResourceSettingsModel, ResourceSettingsPanel
from .setting import ConfigurationSettingPanel
from .workchain import workchain_and_builder
from .result import Wannier90ResultsPanel, Wannier90ResultsModel


class PluginOutline(PluginOutline):
    title = 'Wannier functions'


wannier90 = {
    'outline': PluginOutline,
    'configuration': {
        'panel': ConfigurationSettingPanel,
        'model': ConfigurationSettingsModel,
    },
    'resources': {
        'panel': ResourceSettingsPanel,
        'model': ResourceSettingsModel,
    },
    'workchain': workchain_and_builder,
    'result': {
        'panel': Wannier90ResultsPanel,
        'model': Wannier90ResultsModel,
    },
}
