import json
import sys
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_code(f):
    """Reads input file and determines whether it is meant for Gaussian, ORCA, or MRChem.
    Returns tuple of booleans."""
    try:
        with open(f) as file:
            s = file.read()
    except FileNotFoundError:
        return False, False, False

    is_gaussian, is_orca, is_mrchem = False, False, False

    if 'world_prec' in s:
        is_mrchem = True
    elif '*xyz' in s or '* xyz' in s:
        is_orca = True
    elif '#p' in s or '# p' in s:
        is_gaussian = True
    else:
        raise UnknownJonError(f'Code could not be resolved.')

    test = not sum([is_gaussian, is_orca, is_mrchem]) > 1
    assert test, UnknownJonError(f'Multiple codes detected. Sum = {test}')
    return is_gaussian, is_orca, is_mrchem


class UnknownJonError(NameError):
    pass



class Job:
    def __init__(self, config=None, need_files=None, save_files=None):
        self.config = config
        self.ext = '.job'
        self.inputfile = self.config.input + self.config.ext_inp
        self.outputfile = self.config.input + self.config.ext_out
        self.jobfile = self.config.input + self.ext
        self.cluster = self.config.cluster
        self.need_files = need_files if need_files is not None else []
        self.save_files = save_files if save_files is not None else []
        self.environment = self.load_default_environment()
        self.code = None
        self.job = []

    def __str__(self):
        return '\n'.join(self.job)

    def build_job(self):
        pass

    def write(self):
        with open(self.config.input + self.ext, 'w') as f:
            f.write(str(self.config)+'\n')
            f.write(str(self))

    def make_test_files(self):
        pass

    def set_input(self, i):
        self.inputfile = i + self.config.ext_inp
        self.outputfile = i + self.config.ext_out
        self.jobfile = i + self.ext

    @staticmethod
    def load_default_environment():
        try:
            with open(os.path.join(ROOT, 'default_environments.json')) as f:
                return json.loads(f.read())

        except FileNotFoundError:
            sys.exit('Error reading default environments.')


class MRChemJob(Job):
    def __init__(self, store_orbs=None, store_chk=None, init_orbs=None, init_check=None, checkout=None, **kwargs):
        self.store_orbs = store_orbs if store_orbs is not None else False
        self.store_chk = store_chk if store_chk is not None else False
        self.init_orbs = init_orbs if init_orbs is not None else False
        self.init_chk = init_check if init_check is not None else False

        Job.__init__(self, **kwargs)
        self.code = 'mrchem'
        self.job = self.build_job()

    def build_job(self):
        job = ['']
        job.append('module purge')
        for mod in self.environment[self.cluster][self.code]['modules']:
            job.append(f'module load {mod}')

        job.append('')
        job.append(f'cp {self.inputfile} $SCRATCH')

        for f in self.need_files:
            job.append(f'cp {f} $SCRATCH')

        job.append('cd $SCRATCH')
        if self.init_orbs:
            job.append(f'cp -r {self.init_orbs} initial_guess')
        if self.init_chk:
            job.append(f'cp -r {self.init_chk} checkpoint')

        exe = self.environment[self.cluster][self.code]['exe']
        if self.config.hybrid:
            job.append(f'export OMP_NUM_THREADS={self.config.cpus}')
        job.append(f'{exe} --launcher \'srun -n {self.config.ntasks}\' {self.config.input} > {self.outputfile}')
        job.append('')
        job.append(f'savefile {self.outputfile}')
        job.append(f'savefile {self.config.input + "json"}')
        for f in self.save_files:
            job.append(f'savefile {f}')

        if self.store_orbs:
            job.append('')
            job.append(f'DIR=/cluster/projects/{self.config.account}/$(whoami)/MWOrbitals/${{SLURM_JOBID}}')
            job.append(f'mkdir -p $DIR')
            job.append(f'cp orbitals/* $DIR/')
            job.append(f'echo $DIR > ${{SLURM_SUBMIT_DIR}}/{self.config.input}.orbitals')

        if self.store_chk:
            job.append('')
            job.append(f'DIR=/cluster/projects/{self.config.account}/$(whoami)/MWCheckpoints/${{SLURM_JOBID}}')
            job.append(f'mkdir -p $DIR')
            job.append(f'cp checkpoint/* $DIR/')
            job.append(f'echo $DIR > ${{SLURM_SUBMIT_DIR}}/{self.config.input}.checkpoint')

        job.append('')
        job.append('exit 0')

        return job

    def make_test_files(self, fname='mrchem_test'):
        self.set_input(fname)
        i = ['world_prec = 1.0e-3',
             'Molecule{',
             '  multiplicity = 1',
             '  charge = 0',
             '  $coords',
             '    He 0.0 0.0 0.0',
             '  $end',
             '}',
             'WaveFunction {',
             '  method = pbe',
             '}']

        c = self.config
        c.timelimit = '10:00'
        c.qos = 'Devel'
        c.hybrid = True
        c.input = fname
        c.dev = True
        c.loc = False
        c.ntasks = 2
        c.cpus = 4
        c.build_config()

        with open(fname + self.config.ext_inp, 'w') as f:
            f.write('\n'.join(i))

        with open(fname + self.ext, 'w') as f:
            f.write('\n'.join(c.config + self.build_job()))


class GaussianJob(Job):
    def __init__(self, **kwargs):
        Job.__init__(self, **kwargs)

        self.code = 'gaussian'
        self.job = self.build_job()

    def build_job(self):
        job = ['']
        job.append(f'module purge')
        for mod in self.environment[self.cluster][self.code]['modules']:
            job.append(f'module load {mod}')

        job.append(f'')
        job.append(f'cp {self.inputfile} $SCRATCH')

        for f in self.need_files:
            job.append(f'cp {f} $SCRATCH')

        job.append(f'cd $SCRATCH')
        exe = self.environment[self.cluster][self.code]['exe']
        job.append(f'{exe} {self.inputfile} > {self.outputfile}')
        job.append(f'')
        job.append(f'savefile {self.outputfile}')
        job.append(f'savefile {self.config.input + ".chk"}')
        for f in self.save_files:
            job.append(f'savefile {f}')

        job.append(f'')
        job.append(f'exit 0')
        return job

    def make_test_files(self, fname='gaussian_test'):
        self.set_input(fname)
        i = ['#p pbepbe/6-31G',
             '',
             'Test input',
             '',
             '0 1',
             'He 0.0 0.0 0.0',
             '\n']

        c = self.config
        c.timelimit = '10:00'
        c.qos = 'Devel'
        c.hybrid = False
        c.input = fname
        c.dev = True
        c.loc = True
        c.nodes = 1
        c.ntasks = 8
        c.build_config()

        with open(fname + self.config.ext_inp, 'w') as f:
            f.write('\n'.join(i))

        with open(fname + self.ext, 'w') as f:
            f.write('\n'.join(c.config + self.build_job()))

class ORCAJob(Job):
    def __init__(self, **kwargs):
        Job.__init__(self, **kwargs)
        self.code = 'orca'
        self.job = self.build_job()

    def build_job(self):
        job = ['']
        job.append(f'module purge')
        for mod in self.environment[self.cluster][self.code]['modules']:
            job.append(f'module load {mod}')

        job.append('')
        job.append(f'ORCA={self.environment[self.cluster][self.code]["exe"]}')
        job.append(f'MPI={self.environment[self.cluster][self.code]["mpi"]}')

        job.append(f'')
        job.append(f'export PATH=$PATH:$ORCA')
        job.append(f'export PATH=$PATH:$MPI')
        job.append(f'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORCA')
        job.append(f'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$MPI')
        job.append(f'export RSH_COMMAND="/usr/bin/ssh -x"')

        job.append(f'')
        job.append(f'cp {self.inputfile} $SCRATCH')
        for f in self.need_files:
            job.append(f'cp {f} $SCRATCH')

        job.append(f'cd $SCRATCH')
        job.append(f'$ORCA/orca {self.inputfile} > {self.outputfile}')

        job.append(f'')
        job.append(f'savefile {self.outputfile}')
        job.append(f'savefile *.hess')
        job.append(f'savefile *.gbw')
        job.append(f'savefile *.xyz')
        for f in self.save_files:
            job.append(f'savefile {f}')

        job.append(f'')
        job.append(f'exit 0')
        return job

    def make_test_files(self, fname='orca_test'):
        self.set_input(fname)

        c = self.config
        c.timelimit = '10:00'
        c.qos = 'Devel'
        c.hybrid = False
        c.input = fname
        c.dev = True
        c.loc = False
        c.ntasks = 8
        c.build_config()

        i = ['! pbe 6-31G',
             f'%pal nprocs {c.ntasks} end',
             '* xyz 0 1',
             '  He 0.0 0.0 0.0',
             '*',
             '']

        with open(fname + self.config.ext_inp, 'w') as f:
            f.write('\n'.join(i))

        with open(fname + self.ext, 'w') as f:
            f.write('\n'.join(c.config + self.build_job()))
