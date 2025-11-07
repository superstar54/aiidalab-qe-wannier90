"""Panel for Wannier90 plugin."""

from aiidalab_qe.common.code.model import CodeModel, PwCodeModel
from aiidalab_qe.common.panel import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


class ResourceSettingsModel(PluginResourceSettingsModel):
    """Model for the wannier90 code setting plugin."""

    title = 'Wannier functions'
    identifier = 'wannier90'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_models(
            {
                'pw': PwCodeModel(
                    name='pw.x',
                    description='pw.x',
                    default_calc_job_plugin='quantumespresso.pw',
                ),
                'projwfc': CodeModel(
                    name='projwfc.x',
                    description='projwfc.x',
                    default_calc_job_plugin='quantumespresso.projwfc',
                ),
                'pw2wannier90': CodeModel(
                    name='pw2wannier90.x',
                    description='pw2wannier90.x',
                    default_calc_job_plugin='quantumespresso.pw2wannier90',
                ),
                'wannier90': CodeModel(
                    name='wannier90.x',
                    description='wannier90.x',
                    default_calc_job_plugin='wannier90.wannier90',
                ),
                'skeaf': CodeModel(
                    name='skeaf_v1p3p0_r149',
                    description='skeaf_v1p3p0_r149',
                    default_calc_job_plugin='skeaf.skeaf',
                ),
                'wan2skeaf': CodeModel(
                    name='wan2skeaf.jl',
                    description='wan2skeaf.jl',
                    default_calc_job_plugin='skeaf.wan2skeaf',
                ),

            }
        )


class ResourceSettingsPanel(
    PluginResourceSettingsPanel[ResourceSettingsModel],
):
    """Panel for configuring the wannier90 plugin."""
