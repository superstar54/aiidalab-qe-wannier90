from aiida_quantumespresso.common.types import ElectronicType, SpinType
from .wannier90_workchain import QeAppWannier90BandsWorkChain
from aiida_wannier90_workflows.common.types import WannierProjectionType, WannierFrozenType

def check_codes(codes):
    """Check that the codes are installed on the same computer."""
    if (len({code.computer.pk for code in codes.values()})!= 1):
        raise ValueError(
            'All selected codes must be installed on the same computer. This is because the '
            'calculations rely on large files that are not retrieved by AiiDA.'
        )


def get_builder(codes, structure, parameters, **kwargs):
    from copy import deepcopy

    wannier90_parameters = deepcopy(parameters['wannier90'])
    exclude_semicore=wannier90_parameters.pop('exclude_semicore')
    plot_wannier_functions=wannier90_parameters.pop('plot_wannier_functions')
    retrieve_hamiltonian=wannier90_parameters.pop('retrieve_hamiltonian')
    retrieve_matrices=wannier90_parameters.pop('retrieve_matrices')
    projection_type=wannier90_parameters.pop('projection_type')
    frozen_type=wannier90_parameters.pop('frozen_type')

    all_codes = {
                'pw': codes.get('pw')['code'],
                'pw2wannier90': codes.get('pw2wannier90')['code'],
                'projwfc': codes.get('projwfc')['code'],
                'wannier90': codes.get('wannier90')['code'],
            }
    if plot_wannier_functions:
        all_codes['python'] = codes.get('python')['code']
    check_codes(all_codes)
    protocol = parameters['workchain']['protocol']
    protocol_map = {
        'balanced': 'moderate',
        'stringent': 'precise'
    }
    protocol = protocol_map.get(protocol, protocol)
    overrides = {
        'pw_bands': {
            'scf': deepcopy(parameters['advanced']),
            'bands': deepcopy(parameters['advanced']),
        },
        'wannier90_bands': {
            'nscf': deepcopy(parameters['advanced']),
            'wannier90_parameters': wannier90_parameters,
        },
    }
    parallelization = {
        'num_machines': codes['pw']['nodes'],
        'num_mpiprocs_per_machine': codes['pw']['ntasks_per_node'],
    }
    builder = QeAppWannier90BandsWorkChain.get_builder_from_protocol(
        codes=all_codes,
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        parallelization=parallelization,
        exclude_semicore=exclude_semicore,
        plot_wannier_functions=plot_wannier_functions,
        electronic_type=ElectronicType(parameters['workchain']['electronic_type']),
        spin_type=SpinType(parameters['workchain']['spin_type']),
        initial_magnetic_moments=parameters['advanced']['initial_magnetic_moments'],
        projection_type=WannierProjectionType(projection_type),
        frozen_type=WannierFrozenType(frozen_type),
        retrieve_hamiltonian=retrieve_hamiltonian,
        retrieve_matrices=retrieve_matrices,
        **kwargs,
    )
    return builder


def update_inputs(inputs, ctx):
    """Update the inputs using context."""
    inputs.structure = ctx.current_structure


workchain_and_builder = {
    'workchain': QeAppWannier90BandsWorkChain,
    'exclude': ('structure', 'relax'),
    'get_builder': get_builder,
    'update_inputs': update_inputs,
}
