#!/usr/bin/env python3

import os
import sys
import subprocess

from config import Config
from jobs import Job, MRChemJob, GaussianJob, ORCAJob, resolve_code
from cli import cli

AFFIRMATIVE = ['', 'y', 'yes']


def debug(s, do=False):
    if do:
        sys.stdout.write(s+'\n')


if __name__ == '__main__':
    # Initialize argument parser
    parser = cli()
    args = parser.parse_args()

    testing = True if any([args.test_gaussian, args.test_orca, args.test_mrchem]) else False

    # Manually convert convenience timelimit units to slurm format
    if args.stime is not None:
        timelimit = args.stime
    else:
        timelimit = f'{args.days}-{args.hours}:{args.minutes}:{args.seconds}'
        if timelimit == '00-00:00:00':
            debug('Warning: Walltime set to zero', not testing)

    # Initialize the slurm configuration
    config = Config(loc=args.loc,
                    hybrid=args.hybrid,
                    input=args.input,
                    account=args.account,
                    timelimit=timelimit,
                    memory=args.memory,
                    memtype=args.memtype,
                    nodes=args.nodes,
                    ntasks=args.ntasks,
                    cpus=args.cpus,
                    mail=args.mail,
                    partition=args.partition,
                    cluster=args.cluster,
                    dev=args.devel,
                    exclusive=args.exclusive)

    # Check if testing was required. Exit program if any test requested.
    if args.test_gaussian:
        job = GaussianJob(config=config)
        job.make_test_files()
        debug('Gaussian test files generated.', args.verbose)
    if args.test_orca:
        job = ORCAJob(config=config)
        job.make_test_files()
        debug('ORCA test files generated.', args.verbose)
    if args.test_mrchem:
        job = MRChemJob(config=config)
        job.make_test_files()
        debug('MRChem test files generated.', args.verbose)
    if any([args.test_gaussian, args.test_orca, args.test_mrchem]):
        sys.exit()

    # Read input and determine the code
    # Then construct the job classes
    g, o, m = resolve_code(config.input + config.ext_inp)
    if g:
        debug(f'Gaussian input detected', args.verbose)
        job = GaussianJob(config=config,
                          need_files=args.copy_to,
                          save_files=args.copy_back)
    elif o:
        debug(f'ORCA input detected', args.verbose)
        job = ORCAJob(config=config,
                      need_files=args.copy_to,
                      save_files=args.copy_back)
    elif m:
        debug(f'MRChem input detected', args.verbose)
        job = MRChemJob(config=config,
                        store_orbs=not args.rm_orb,
                        store_chk=not args.rm_check,
                        init_orbs=args.guess_orb,
                        init_check=args.guess_check,
                        need_files=args.copy_to,
                        save_files=args.copy_back)
    else:
        debug('Code not determined', args.verbose)
        job = Job(config=config)

    # Write job files
    if os.path.exists(job.jobfile):
        if args.force:
            job.write()
            debug(f'File written to {job.jobfile}', args.verbose)
        else:
            if input(f'Job file <{job.jobfile}> exists. Overwrite? ([y]/n) ') in AFFIRMATIVE:
                job.write()
                debug(f'File written to {job.jobfile}', args.verbose)
            else:
                sys.exit('Aborted')
    else:
        job.write()
        debug(f'File written to {job.jobfile}', args.verbose)

    if args.execute:
        subprocess.call(['sbatch', job.jobfile])

