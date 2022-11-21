# PySlurm
Use python to generate SLURM job files for Saga, Fram, and Betzy.

## Setup
Run `setup.py` to add the script to your `PATH`:

```
python setup.py
```

## Dependencies
The scripts should run with a standard Python installation, no external modules needed.

## Usage
```
usage: pyslurm.py [-h] [-v] [-f] [-i INPUT] [-o OUTPUT] [-d DEST] [-I ID]
                  [-s SUFFIX] [-c {saga,fram,betzy}] [-X]
                  [--code {orca,gaussian,mrchem}] [-n NODES] [-nt NTASKS]
                  [-nc CPUS] [-a ACCOUNT] [-m MEMORY] [-mt {tot,cpu}]
                  [--stime STIME] [--hours HOURS] [--days DAYS]
                  [--minutes MINUTES] [--seconds SECONDS] [-em MAIL]
                  [-p PARTITION] [-q QOS] [-D] [-H] [-L] [-E]
                  [--display-name DISPLAY_NAME] [-V VERSION] [--json]
                  [--guess-orb PATH] [--guess-check PATH] [--rm-orb]
                  [--rm-check] [-cpt PATH [PATH ...]] [-cpb PATH [PATH ...]]
                  [--test-gaussian] [--test-orca] [--test-mrchem]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print extra information.
  -f, --force           Do not ask when overwriting files.

Job related arguments:
  -i INPUT, --input INPUT
                        Name of input file
  -o OUTPUT, --output OUTPUT
                        Name of output file
  -d DEST, --dest DEST  Path to job directory
  -I ID, --identifier ID
                        Job name shown in the queue
  -s SUFFIX, --suffix SUFFIX
                        Suffix appended to job name in queue
  -c {saga,fram,betzy}, --cluster {saga,fram,betzy}
                        Which cluster to submit to.
  -X, --execute         Submit job to the queue
  --code {orca,gaussian,mrchem}
                        QC code input was made for

SLURM related arguments.:
  -n NODES, --nodes NODES
                        Number of nodes.
  -nt NTASKS, --ntasks NTASKS
                        Number of tasks / tasks-per-node.
  -nc CPUS, --cpus CPUS
                        Number of CPUs per task.
  -a ACCOUNT, --account ACCOUNT
                        Account to be billed.
  -m MEMORY, --memory MEMORY
                        How much memory to request, incl. units.
  -mt {tot,cpu}, --memtype {tot,cpu}
                        Specify the type of memory requirements.
  --stime STIME         Walltime in slurm format for the job.
  --hours HOURS         Walltime in hours for the job.
  --days DAYS           Walltime in days for the job.
  --minutes MINUTES     Walltime in minutes for the job.
  --seconds SECONDS     Walltime in seconds for the job.
  -em MAIL, --mail MAIL
                        Email notifications.
  -p PARTITION, --partition PARTITION
                        Which cluster partition to use.
  -q QOS, --qos QOS     Quality of Service.
  -D, --devel           Request development job.
  -H, --hybrid          Hybrid OMP+MPI parallel scheme.
  -L, --loc             Explicitply request number of nodes.
  -E, --exclusive       Request full nodes (discouraged).
  --display-name DISPLAY_NAME
                        Name used in the SLURM queue (not in file names)

MRChem related arguments:
  -V VERSION, --version VERSION
                        Path to installed mrchem input parser (main
                        executable)
  --json                Pass JSON option to MRChem launcher for JSON input
                        file.
  --guess-orb PATH      Full path to directory holding initial guess orbitals.
                        Will be copied to $SCRATCH/initial_guess.
  --guess-check PATH    Full path to directory holding checkpoint orbitals.
                        Will be copied to $SCRATCH/checkpoint.
  --rm-orb              Do not copy optimized orbitals to storage.
  --rm-check            Do not copy checkpoint orbitals to storage.

Misc. arguments:
  -cpt PATH [PATH ...], --copy-to PATH [PATH ...]
                        Copy file(s) to $SCRATCH.
  -cpb PATH [PATH ...], --copy-back PATH [PATH ...]
                        Copy file(s) back to $SLURM_SUBMIT_DIR.

Test related arguments:
  --test-gaussian       Generate test inputs for Gaussian.
  --test-orca           Generate test inputs for ORCA.
  --test-mrchem         Generate test inputs for MRChem.
```

Example call where SLURM job files are generated for all input files in the current directory. NREL MW orbitals are read from files that contain a path where the orbitals actually are stored (somewhere in `cluster/projects` due to size)

```
ls *.inp | while read INP; do JOB=$(echo $INP | cut -d"." -f1); ORBS=$(cat ../calcs_mw_nrel/${JOB}.orbitals); pyslurm.py -i $INP --cluster saga -nc 16 -nt 12 -m 140GB --hours 24 --hybrid --account $(accHylleraas) --json -X -f --guess-orb $ORBS; done


```
