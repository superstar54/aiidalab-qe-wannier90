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

        # error message
        self.error_message = ipw.HTML()
        # Warning message
        self.warning_message = ipw.HTML(
            """<div style="color: blue; font-weight: bold; border: 1px solid red; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            ⚠️ This plugin requires the Wannier90 code from the latest source code from the <a href="https://github.com/wannier-developers/wannier90" target="_blank">Wannier90 GitHub repository</a>.
            </div>"""
        )

        self._model.observe(
            self._on_electronic_type_change,
            'electronic_type',
        )

    def render(self):

        if self.rendered:
            return

        # Workflow explanation
        workflow_explanation = ipw.HTML(
            """<details style="margin-bottom: 10px;">
            <summary style="font-weight: bold;">📘 Workflow Overview</summary>
            <div style="padding-left: 10px; margin-top: 5px;">
            This workflow consists of two main steps:
            <ul>
                <li><strong>Step 1:</strong> Run a <code>PwBandsWorkChain</code> to compute the SCF charge density and PW bands.</li>
                <li><strong>Step 2:</strong> Use the SCF charge density as input for <code>Wannier90OptimizeWorkChain</code>. It will compare with PW bands internally and output a value <code>bands_distance</code> (typically good if ≤ 30 meV).</li>
            </ul>
            </div>
            </details>"""
        )

        self.exclude_semicore = ipw.Checkbox(
            value=self._model.exclude_semicore,
            description='Exclude semicore',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'exclude_semicore'),
            (self.exclude_semicore, 'value'),
        )
        self.retrieve_hamiltonian = ipw.Checkbox(
            value=self._model.retrieve_hamiltonian,
            description='Retrieve Hamiltonian',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'retrieve_hamiltonian'),
            (self.retrieve_hamiltonian, 'value'),
        )
        self.retrieve_matrices = ipw.Checkbox(
            value=self._model.retrieve_matrices,
            description='Retrieve Hamiltonian',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'retrieve_matrices'),
            (self.retrieve_matrices, 'value'),
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
            self.error_message,
            self.warning_message,
            InAppGuide(identifier='wannier90-settings'),
            workflow_explanation,
            self.exclude_semicore,
            self.plot_wannier_functions,
            self.retrieve_hamiltonian,
            self.projection_type,
            self.frozen_type,
            self.number_of_disproj_max,
            self.number_of_disproj_min,
        ]
        self.rendered = True

    def _on_electronic_type_change(self, change):
        if change['new'] == 'insulator':
            self.error_message.value = """<div style="color: red; font-weight: bold; border: 1px solid red; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            ⚠️ Electronic type: Insulator setting is not supported yet. You can still use the Metal setting even if your material is an insulator.
            </div>"""
