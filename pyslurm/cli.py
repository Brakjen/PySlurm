import argparse


def cli():
    parser = argparse.ArgumentParser()

    # Top level parser arguments
    parser.add_argument('-v', '--verbose', action='store_true', help='Print extra information.')
    parser.add_argument('-f', '--force', action='store_true', help='Do not ask when overwriting files.')

    # Job related arguments
    job = parser.add_argument_group('Job related arguments')
    job.add_argument('-i', '--input', type=str, help='Name of input file')
    job.add_argument('-o', '--output', type=str, help='Name of output file')
    job.add_argument('-d', '--dest', default='.', type=str, help='Path to job directory')
    job.add_argument('-I', '--identifier', dest='id', type=str, help='Job name shown in the queue')
    job.add_argument('-s', '--suffix', type=str, help='Suffix appended to job name in queue')
    job.add_argument('-c', '--cluster', choices=['saga', 'fram', 'betzy'], type=str, help='Which cluster to submit to.')
    job.add_argument('-X', '--execute', action='store_true', help='Submit job to the queue')
    job.add_argument('--code', type=str, choices=['orca', 'gaussian', 'mrchem'], help='QC code input was made for')

    # SLURM related arguments
    slurm = parser.add_argument_group('SLURM related arguments.')
    slurm.add_argument('-n', '--nodes', help='Number of nodes.')
    slurm.add_argument('-nt', '--ntasks', help='Number of tasks / tasks-per-node.')
    slurm.add_argument('-nc', '--cpus', help='Number of CPUs per task.')
    slurm.add_argument('-a', '--account', help='Account to be billed.')
    slurm.add_argument('-m', '--memory', help='How much memory to request, incl. units.')
    slurm.add_argument('-mt', '--memtype', choices=['tot', 'cpu'], help='Specify the type of memory requirements.')
    slurm.add_argument('--stime', type=str, help='Walltime in slurm format for the job.')
    slurm.add_argument('--hours', default='00', type=str,  help='Walltime in hours for the job.')
    slurm.add_argument('--days', default='00', type=str,  help='Walltime in days for the job.')
    slurm.add_argument('--minutes', default='00', type=str,  help='Walltime in minutes for the job.')
    slurm.add_argument('--seconds', default='00', type=str,  help='Walltime in seconds for the job.')
    slurm.add_argument('-em', '--mail', help='Email notifications.')
    slurm.add_argument('-p', '--partition', help='Which cluster partition to use.')
    slurm.add_argument('-q', '--qos', help='Quality of Service.')
    slurm.add_argument('-D', '--devel', action='store_true', help='Request development job.')
    slurm.add_argument('-H', '--hybrid', action='store_true', help='Hybrid OMP+MPI parallel scheme.')
    slurm.add_argument('-L', '--loc', action='store_true', help='Explicitply request number of nodes.')
    slurm.add_argument('-E', '--exclusive', action='store_true', help='Request full nodes (discouraged).')

    # MRChem related arguments
    mrc = parser.add_argument_group('MRChem related arguments')
    mrc.add_argument('-V', '--version', type=str, help='Path to installed mrchem input parser (main executable)')
    mrc.add_argument('--json', action='store_true', help='Pass JSON option to MRChem launcher for JSON input file.')
    mrc.add_argument('--guess-orb', type=str, metavar='PATH', help='Full path to directory holding initial guess orbitals. Will be copied to $SCRATCH/initial_guess.')
    mrc.add_argument('--guess-check', type=str, metavar='PATH', help='Full path to directory holding checkpoint orbitals. Will be copied to $SCRATCH/checkpoint.')
    mrc.add_argument('--rm-orb', action='store_true', help='Do not copy optimized orbitals to storage.')
    mrc.add_argument('--rm-check', action='store_true', help='Do not copy checkpoint orbitals to storage.')

    # Misc arguments
    misc = parser.add_argument_group('Misc. arguments')
    misc.add_argument('-cpt', '--copy-to', nargs='+', type=str, metavar='PATH', help='Copy file(s) to $SCRATCH.')
    misc.add_argument('-cpb', '--copy-back', nargs='+', type=str, metavar='PATH', help='Copy file(s) back to $SLURM_SUBMIT_DIR.')

    # Test related arguments
    test = parser.add_argument_group('Test related arguments')
    test.add_argument('--test-gaussian', action='store_true', help='Generate test inputs for Gaussian.')
    test.add_argument('--test-orca', action='store_true', help='Generate test inputs for ORCA.')
    test.add_argument('--test-mrchem', action='store_true', help='Generate test inputs for MRChem.')

    return parser
