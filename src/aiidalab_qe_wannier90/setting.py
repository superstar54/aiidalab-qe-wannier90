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
                ⚠️ This plugin requires the Wannier90 code from the latest source code from the
                <a href="https://github.com/wannier-developers/wannier90" target="_blank" style="color: red; font-weight: bold; text-decoration: underline;">Wannier90 GitHub repository</a>.
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
                <li><strong>Step 1:</strong> Run a Quantum ESPRESSO workflow (<code>PwBandsWorkChain</code>) to compute the self-consistent (SCF) DFT charge density and corresponding DFT band structure along a standard path.</li>
                <li><strong>Step 2:</strong> Use the SCF charge density as input for the Wannierization workflow, using the Wannier90 code (<code>Wannier90OptimizeWorkChain</code>). The workflow will compute maximally localized Wannier functions (MLWFs) and compare the interpolated bands with the DFT bands internally. The corresponding band distance <code>η</code> is one of the outputs and is a measure of the interpolation quality (typically good if <code>η ≤ 30</code> meV).</li>
            </ul>
            </div>
            </details>"""
        )


        self.exclude_semicore = ipw.Checkbox(
            value=self._model.exclude_semicore,
            description='Exclude semicore states',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'exclude_semicore'),
            (self.exclude_semicore, 'value'),
        )
        self.retrieve_hamiltonian = ipw.Checkbox(
            value=self._model.retrieve_hamiltonian,
            description="Retrieve real-space Hamiltonian ('.tb' file)",
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
        # ---------------------------------------------------------------------------
        self.algorithm_description = ipw.HTML(
            """<details style="margin-bottom: 10px;">
            <summary style="font-weight: bold;">📘 Automated Wannierization algorithm</summary>
            You can select some variants of the automated Wannierization algorithm.
            The recommended choice is to use the PDWF algorithm described in
            <a href="https://www.nature.com/articles/s41524-023-01146-w" target="_blank">[J. Qiao, G. Pizzi, N. Marzari, … (2023)]</a>:
            “Pseudoatomic orbitals from pseudopotential” as starting projections, and “Projectability + energy window”
            for the frozen states selection.
            </details>
            """
        )
        self.projection_description = ipw.HTML(
            """<details style="margin-bottom: 10px;">
            <summary style="font-weight: bold;">📘 Starting projections</summary>
            <ul>
                <li><b>Pseudoatomic orbitals from pseudopotential (PDWF method)</b> (recommended)</li>
                <li><b>Selected columns of the density matrix (SCDM)</b></li>
            </ul>
            </details>
            """
        )

        # Dropdown for Projection Type
        self.projection_type = ipw.Dropdown(
            options=[
                ('Pseudoatomic orbitals from pseudopotential (PDWF method)', 'atomic_projectors_qe'),
                ('Selected columns of the density matrix (SCDM)', 'SCDM'),
                # ('Analytical hydrogenic rbitals', 'analytic'),  # Hidden for now
            ],
            value='atomic_projectors_qe',
            description='Starting projections:',
            style={'description_width': 'initial'},
        )

        # Layout the widgets
        self.projection_selection_widget = ipw.VBox([
            self.projection_description,
            self.projection_type
        ])

        ipw.link(
            (self._model, 'projection_type'),
            (self.projection_type, 'value'),
        )
        # ---------------------------------------------------------------------------
        # Description HTML
        self.description_html = ipw.HTML(
            """<details style="margin-bottom: 10px;">
            <summary style="font-weight: bold;">📘 Frozen states</summary>
            <ul>
                <li><b>Projectability + energy window</b> (recommended, PDWF method
                <a href="o" target="_blank">[Junfeng’s paper]</a>)
                is a combination of the two methods below (as long as one of the two criteria is satisfied, the state is frozen).</li>
                <li><b>Projectability only</b> will freeze all states with projectability larger than a threshold value
                (that is internally optimized by the workflow).</li>
                <li><b>Energy window only</b> will freeze all states whose energy is smaller or equal than E<sub>F</sub> +
                <span id="energy-window-value">2</span> eV, where E<sub>F</sub> is the Fermi level.</li>
            </ul>
            """
        )

        # Dropdown for Frozen Type
        self.frozen_type = ipw.Dropdown(
            options=[
                ('Projectability + energy window', 'fixed_plus_projectability'),
                ('Projectability only', 'projectability'),
                ('Energy window only', 'energy_fixed'),
            ],
            value='fixed_plus_projectability',
            description='Frozen states:',
            style={'description_width': 'initial'},
        )

        # Energy Window Input (default 2 eV)
        self.energy_window_label = ipw.HTML(
            'Energy window upper limit (eV above <b>E<sub>F</sub></b>):'
        )

        self.energy_window_input = ipw.FloatText(value=2.0,
                                                    description='',
                                                    layout=ipw.Layout(width='50px'),)
        self.energy_window_widget = ipw.HBox(children=[self.energy_window_label, self.energy_window_input],
                                             layout=ipw.Layout(width='100%'))

        # Attach the event listener
        self.frozen_type.observe(self._update_energy_window_visibility, names='value')

        # Initialize visibility
        self._update_energy_window_visibility({'new': self.frozen_type.value})

        # Layout the widgets
        self.frozen_states_widget = ipw.VBox([
            self.description_html,
            self.frozen_type,
            self.energy_window_widget,
        ])
        self.frozen_type = ipw.Dropdown(
            options=['fixed_plus_projectability', 'projectability', 'energy_fixed'],
            value=self._model.frozen_type,
            description='Frozen states: ',
            style={'description_width': 'initial'},
        )
        ipw.link(
            (self._model, 'frozen_type'),
            (self.frozen_type, 'value'),
        )
        # ---------------------------------------------------------------------------
        self.children = [
            self.error_message,
            self.warning_message,
            InAppGuide(identifier='wannier90-settings'),
            workflow_explanation,
            self.exclude_semicore,
            self.plot_wannier_functions,
            self.retrieve_hamiltonian,
            self.algorithm_description,
            self.projection_selection_widget,
            self.frozen_states_widget,
            # self.number_of_disproj_max,
            # self.number_of_disproj_min,
        ]
        self.rendered = True

    def _on_electronic_type_change(self, change):
        if change['new'] == 'insulator':
            self.error_message.value = """<div style="color: red; font-weight: bold; border: 1px solid red; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            ⚠️ Electronic type: Insulator setting is not supported yet. You can still use the Metal setting even if your material is an insulator.
            </div>"""
        else:
            self.error_message.value = ''

    # Function to toggle the visibility of the energy window input
    def _update_energy_window_visibility(self, change):
        if change['new'] in ['fixed_plus_projectability', 'energy_fixed']:
            self.energy_window_widget.layout.display = 'block'
        else:
            self.energy_window_widget.layout.display = 'none'
