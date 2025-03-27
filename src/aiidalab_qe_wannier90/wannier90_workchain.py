import numpy as np
from aiida import orm
from aiida.engine import WorkChain, if_
from aiida_wannier90_workflows.workflows.bands import Wannier90BandsWorkChain
from aiida_wannier90_workflows.workflows.optimize import Wannier90OptimizeWorkChain
from aiida_quantumespresso.workflows.pw.bands import PwBandsWorkChain
from aiida_wannier90_workflows.utils.workflows.builder.setter import set_parallelization
from aiida_pythonjob.launch import prepare_pythonjob_inputs
from aiida_pythonjob import PythonJob
from .utils import process_xsf_files
class QeAppWannier90BandsWorkChain(WorkChain):
    """Workchain to run a bands calculation with Quantum ESPRESSO and Wannier90."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.input('structure', valid_type=orm.StructureData)
        spec.input('protocol', valid_type=orm.Str)
        spec.input_namespace('codes', valid_type=orm.Code, dynamic=True)
        spec.input_namespace('overrides', dynamic=True, required=False)
        spec.input_namespace('kwargs', dynamic=True, required=False)
        spec.input('parallelization', valid_type=orm.Dict, required=False)
        spec.expose_outputs(
            PwBandsWorkChain,
            namespace='pw_bands',
            namespace_options={
                'required': False,
                'help': 'Outputs of the `PwBandsWorkChain`.',
            },
        )
        spec.expose_outputs(
            Wannier90OptimizeWorkChain,
            namespace='wannier90_bands',
            namespace_options={
                'required': False,
                'help': 'Outputs of the `Wannier90OptimizeWorkChain`.',
            },
        )
        spec.output_namespace('generate_isosurface', required=False, dynamic=True)

        spec.outline(cls.setup,
                     cls.run_bands,
                     cls.inspect_pw_bands,
                     cls.run_optimize,
                     cls.inspect_optimize,
                     if_(cls.should_run_generate_isosurface)(
                         cls.generate_isosurface,
                         cls.inspect_generate_isosurface
                     ),
                     )

        spec.exit_code(
            400, 'ERROR_PW_BANDS_WORKCHAIN_FAILED', message='The pw bands workchain failed.'
        )
        spec.exit_code(
            401, 'ERROR_WANNIER90_BANDS_WORKCHAIN_FAILED', message='The wannier90 bands workchain failed.'
        )

    @classmethod
    def get_builder_from_protocol(
        cls,
        codes,
        structure,
        protocol=None,
        parallelization=None,
        overrides=None,
        **kwargs,
    ):
        """Return a BandsWorkChain builder prepopulated with inputs following the specified protocol

        :param codes: the codes required by the workchain.
        :param structure: the ``StructureData`` instance to use.
        :param protocol: protocol to use, if not specified, the default will be used.

        """

        builder = cls.get_builder()
        builder.codes = codes
        builder.structure = structure
        builder.protocol = protocol
        if overrides:
            builder.overrides = overrides
        if kwargs:
            builder.kwargs = kwargs
        if parallelization:
            builder.parallelization = parallelization
        return builder

    def setup(self):
        """Define the current workchain"""
        pass

    def run_bands(self):
        """Run the bands workchain"""
        if 'overrides' in self.inputs:
            overrides = self.inputs.overrides.get('pw_bands', {})
        else:
            overrides = {}
        kwargs = self.inputs.kwargs if 'kwargs' in self.inputs else {}
        builder = PwBandsWorkChain.get_builder_from_protocol(
            code = self.inputs.codes['pw'],
            structure = self.inputs.structure,
            protocol = self.inputs.protocol.value,
            overrides = overrides,
            **kwargs,
        )
        builder.pop('relax')
        builder.metadata.call_link_label = 'pw_bands'
        if 'parallelization' in self.inputs:
            set_parallelization(
                builder, self.inputs.parallelization.get_dict(), process_class=PwBandsWorkChain
            )
        node = self.submit(builder)
        self.report(f'submitting `WorkChain` <PK={node.pk}>')
        self.to_context(**{'pw_bands': node})

    def inspect_pw_bands(self):
        """Inspect the results of the bands workchain"""
        workchain = self.ctx['pw_bands']

        if not workchain.is_finished_ok:
            self.report('Pw bands workchain failed')
            return self.exit_codes.ERROR_WORKCHAIN_FAILED
        else:
            self.out_many(
                self.exposed_outputs(
                    self.ctx['pw_bands'], PwBandsWorkChain, namespace='pw_bands'
                )
            )
            self.report('Pw bands workchain completed successfully')

    def run_optimize(self):
        """Run the optimize workchain"""
        pw_bands_node = self.ctx.pw_bands
        if not pw_bands_node.is_finished_ok:
            self.report('Bands workchain failed')
            return self.exit_codes.ERROR_WORKCHAIN_FAILED
        scf_calc = pw_bands_node.outputs.scf_parameters.creator
        parent_folder = scf_calc.outputs.remote_folder
        structure = scf_calc.inputs.structure
        reference_bands = pw_bands_node.outputs.band_structure
        bands_kpoints = reference_bands.creator.inputs.kpoints
        if 'overrides' in self.inputs:
            overrides = self.inputs.overrides.get('wannier90_bands', {})
        else:
            overrides = {}
        wannier90_parameters = overrides.pop('wannier90_parameters', {})
        number_of_disproj_max = wannier90_parameters.pop('number_of_disproj_max', 15)
        number_of_disproj_min = wannier90_parameters.pop('number_of_disproj_min', 2)
        kwargs = self.inputs.kwargs if 'kwargs' in self.inputs else {}
        codes = {key: value for key, value in self.inputs.codes.items()}
        builder = Wannier90OptimizeWorkChain.get_builder_from_protocol(
            codes = codes,
            structure = structure,
            protocol = self.inputs.protocol.value,
            reference_bands=reference_bands,
            bands_kpoints=bands_kpoints,
            overrides=overrides,
            **kwargs,
        )
        builder.optimize_disprojmax_range = orm.List(list=list(np.linspace(0.99, 0.85, number_of_disproj_max)))
        builder.optimize_disprojmin_range = orm.List(list=list(np.linspace(0.01, 0.15, number_of_disproj_min)))
        builder.pop('scf')
        builder.nscf.pw.parent_folder = parent_folder
        if 'parallelization' in self.inputs:
            set_parallelization(
                builder, self.inputs.parallelization.get_dict(), process_class=Wannier90BandsWorkChain
            )
        node = self.submit(builder)
        self.report(f'submitting `WorkChain` <PK={node.pk}>')
        self.to_context(**{'wannier90_bands': node})

    def inspect_optimize(self):
        """Attach the bands results"""
        workchain = self.ctx['wannier90_bands']

        if not workchain.is_finished_ok:
            self.report('Optimize workchain failed')
            return self.exit_codes.ERROR_WORKCHAIN_FAILED
        else:
            self.out_many(
                self.exposed_outputs(
                    self.ctx['wannier90_bands'], Wannier90OptimizeWorkChain, namespace='wannier90_bands'
                )
            )
            self.report('Optimize workchain completed successfully')

    def should_run_generate_isosurface(self):
        kwargs = self.inputs.kwargs if 'kwargs' in self.inputs else {}
        return kwargs.get('plot_wannier_functions', False)

    def generate_isosurface(self):
        """Plot the results"""

        workchain = self.ctx['wannier90_bands']
        inputs = prepare_pythonjob_inputs(
            process_xsf_files,
            code = self.inputs.codes['python'],
            output_ports=[{'name': 'atoms'},
                      {'name': 'parameters'},
                      {'name': 'mesh_data', 'identifier': 'namespace'},
                      ],
            parent_folder=workchain.outputs.wannier90_plot.remote_folder,
            computer=workchain.inputs.wannier90.wannier90.code.computer,
            register_pickle_by_value=True,
        )
        node = self.submit(PythonJob, **inputs)
        self.report(f'submitting `PythonJob` <PK={node.pk}>')
        self.to_context(**{'generate_isosurface': node})

    def inspect_generate_isosurface(self):
        """Inspect the results of the generate_isosurface"""
        workchain = self.ctx['generate_isosurface']

        if not workchain.is_finished_ok:
            self.report('Plot workchain failed')
            return self.exit_codes.ERROR_WORKCHAIN_FAILED
        else:
            self.out('generate_isosurface.atoms', workchain.outputs.atoms)
            self.out('generate_isosurface.parameters', workchain.outputs.parameters)
            self.out('generate_isosurface.mesh_data', workchain.outputs.mesh_data)
            self.report('Plot wf completed successfully')
