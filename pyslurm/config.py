import socket


def resolve_cluster():
    """Determine which HPC cluster the code is currently running on."""
    h = socket.gethostname()
    if 'fram.sigma2.no' in h:
        return 'fram'
    elif 'saga.sigma2.no' in h:
        return 'saga'
    elif 'betzy.sigma2.no' in h:
        return 'betzy'
    else:
        return 'saga'


class SlurmSyntaxError(ValueError):
    pass


class Config:
    def __init__(self, loc=False, dev=False, hybrid=False, account=None, timelimit=None, memory=None, nodes=None,
                 ntasks=None, cpus=None, ext_inp=None, ext_out=None, ext_log=None, ext_err=None, mail=None,
                 input=None, partition=None, cluster=None, memtype=None, exclusive=False):

        self.account = account if account is not None else ''
        self.timelimit = timelimit if timelimit is not None else '30:00'
        self.memory = memory if memory is not None else '5GB'
        self.memtype = memtype if memtype is not None else 'tot'
        self.nodes = nodes if nodes is not None else '1'
        self.ntasks = ntasks if ntasks is not None else '16'
        self.cpus = cpus if cpus is not None else '8'
        self.ext_inp = ext_inp if ext_inp is not None else '.inp'
        self.ext_out = ext_out if ext_out is not None else '.out'
        self.ext_err = ext_err if ext_err is not None else '.err'
        self.ext_log = ext_log if ext_log is not None else '.log'
        self.mail = mail if mail is not None else 'None'
        self.loc = loc
        self.dev = dev
        self.input = input if input is not None else 'JobName'
        self.partition = partition if partition is not None else 'Normal'
        self.hybrid = hybrid
        self.qos = 'Devel' if self.dev else None
        self.cluster = cluster if cluster is not None else resolve_cluster()
        self.exclusive = exclusive

        assert self.memory.lower().endswith('b'), 'Invalid memory units'
        if self.ext_inp in self.input:
            self.input = self.input[:-4]

        self.build_config()

    def add_section(self, key, val):
        if val is None:
            self.config.append(f'#SBATCH --{key}')
        else:
            self.config.append(f'#SBATCH --{key}={val}')

    def build_config(self):
        self.config = ['#!/bin/bash', '']
        self.add_section('account', self.account)
        self.add_section('mail-type', self.mail)
        self.add_section('job-name', self.input)
        self.add_section('output', self.input + self.ext_log)
        self.add_section('error', self.input + self.ext_err)
        self.add_section('time', self.timelimit)

        if self.partition != 'Normal':
            self.add_section('partition', self.partition)

        # Development job?
        if self.dev:
            self.add_section('qos', self.qos)

        # Memory specification
        if self.cluster.lower() != 'fram':
            if self.memtype == 'tot':
                self.add_section('mem', self.memory)
            elif self.memtype == 'cpu':
                self.add_section('mem-per-cpu', self.memory)

        if self.exclusive:
            self.add_section('exclusive', None)

        # Determine parallel scheme
        if self.loc:
            self.add_section('nodes', self.nodes)
            self.add_section('ntasks-per-node', self.ntasks)
        else:
            if self.hybrid:
                self.add_section('ntasks', self.ntasks)
                self.add_section('cpus-per-task', self.cpus)
            else:
                self.add_section('ntasks', self.ntasks)

        return self.config

    def __str__(self):
        return '\n'.join(self.config)

    def to_dict(self):
        d = dict(self.__dict__)
        del d['config']
        return d
