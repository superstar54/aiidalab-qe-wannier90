"""Panel for Wannier90 plugin."""

from aiidalab_qe.common.panel import ConfigurationSettingsPanel
import ipywidgets as ipw
from .model import ConfigurationSettingsModel
from aiidalab_qe.common.infobox import InAppGuide


class ConfigurationSettingPanel(
    ConfigurationSettingsPanel[ConfigurationSettingsModel],
):
    def __init__(self, model: ConfigurationSettingsModel, **kwargs):
        super().__init__(model, **kwargs)

    def render(self):
        if self.rendered:
            return

        self.exclude_semicore = ipw.Checkbox(
            value=self._model.exclude_semicore,
            description='Exclude semicore',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'exclude_semicore'),
            (self.exclude_semicore, 'value'),
        )
        self.compute_hamiltonian = ipw.Checkbox(
            value=self._model.compute_hamiltonian,
            description='Compute Hamiltonian',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'compute_hamiltonian'),
            (self.compute_hamiltonian, 'value'),
        )
        self.plot_wannier_functions = ipw.Checkbox(
            value=self._model.plot_wannier_functions,
            description='Compute real-space Wannier functions',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'plot_wannier_functions'),
            (self.plot_wannier_functions, 'value'),
        )
        self.number_of_disproj_max = ipw.IntText(
            value=self._model.number_of_disproj_max,
            description='Number of dis_proj_max',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'number_of_disproj_max'),
            (self.number_of_disproj_max, 'value'),
        )
        self.number_of_disproj_min = ipw.IntText(
            value=self._model.number_of_disproj_min,
            description='Number of dis_proj_min',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'number_of_disproj_min'),
            (self.number_of_disproj_min, 'value'),
        )
        self.projection_type = ipw.Dropdown(
            options=['atomic_projectors_qe', 'SCDM', 'analytic'],
            value=self._model.projection_type,
            description='Projection type',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'projection_type'),
            (self.projection_type, 'value'),
        )
        self.frozen_type = ipw.Dropdown(
            options=['fixed_plus_projectability', 'projectability', 'energy_fixed'],
            value=self._model.frozen_type,
            description='Frozen type',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'frozen_type'),
            (self.frozen_type, 'value'),
        )
        self.children = [
            InAppGuide(identifier='pdos-settings'),
            self.exclude_semicore,
            self.plot_wannier_functions,
            self.compute_hamiltonian,
            self.projection_type,
            self.frozen_type,
            self.number_of_disproj_max,
            self.number_of_disproj_min,
        ]
        self.rendered = True
