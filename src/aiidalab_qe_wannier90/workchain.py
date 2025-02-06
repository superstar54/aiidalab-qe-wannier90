from aiida_quantumespresso.common.types import ElectronicType, SpinType
from .wannier90_workchain import QeAppWannier90BandsWorkChain

def check_codes(pw_code, pw2wannier90_code, projwfc_code, wannier90_code):
    """Check that the codes are installed on the same computer."""
    if (
        not any(
            [
                pw_code is None,
                pw2wannier90_code is None,
                projwfc_code is None,
                wannier90_code is None,
            ]
        )
        and len(
            {
                pw_code.computer.pk,
                pw2wannier90_code.computer.pk,
                projwfc_code.computer.pk,
                wannier90_code.computer.pk,
            }
        )
        != 1
    ):
        raise ValueError(
            'All selected codes must be installed on the same computer. This is because the '
            'calculations rely on large files that are not retrieved by AiiDA.'
        )


def get_builder(codes, structure, parameters, **kwargs):
    from copy import deepcopy

    pw_code = codes.get('pw')['code']
    pw2wannier90_code = codes.get('pw2wannier90')['code']
    projwfc_code = codes.get('projwfc')['code']
    wannier90_code = codes.get('wannier90')['code']
    check_codes(pw_code, pw2wannier90_code, projwfc_code, wannier90_code)
    protocol = parameters['workchain']['protocol']

    scf_overrides = deepcopy(parameters['advanced'])
    nscf_overrides = deepcopy(parameters['advanced'])
    wannier90_parameters = deepcopy(parameters['wannier90'])

    overrides = {
        'nscf': nscf_overrides,
        'scf': scf_overrides,
    }
    parallelization = {
        'num_machines': codes['pw']['nodes'],
        'num_mpiprocs_per_machine': codes['pw']['ntasks_per_node'],
    }
    builder = QeAppWannier90BandsWorkChain.get_builder_from_protocol(
        codes={
                'pw': pw_code,
                'pw2wannier90': pw2wannier90_code,
                'projwfc': projwfc_code,
                'wannier90': wannier90_code
            },
        structure=structure,
        protocol=protocol,
        overrides=overrides,
        parallelization=parallelization,
        exclude_semicore=wannier90_parameters['exclude_semicore'],
        plot_wannier_functions=wannier90_parameters['plot_wannier_functions'],
        electronic_type=ElectronicType(parameters['workchain']['electronic_type']),
        spin_type=SpinType(parameters['workchain']['spin_type']),
        initial_magnetic_moments=parameters['advanced']['initial_magnetic_moments'],
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
