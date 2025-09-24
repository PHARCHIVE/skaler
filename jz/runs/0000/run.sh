#!/bin/bash

## BEGIN SBATCH directives
#SBATCH --job-name=0000
#SBATCH --output=0000.txt
#SBATCH --ntasks=80
#SBATCH --ntasks-per-node=40
#SBATCH --hint=nomultithread
#SBATCH --time=20:00:00
#SBATCH --partition=cpu_p1
#SBATCH --account=xzy@cpu
#SBATCH --mail-type=ALL
#SBATCH --mail-user=philip.deegan@lpp.polytechnique.fr
## END SBATCH directives

set -exu

module load gcc/12.2.0 cmake/3.21.3 python/3.11.5 hdf5/1.12.0-mpi openmpi/4.1.8

CWD="/lustre/fswork/projects/rech/wrb/usv98cr/skale/runs/0000"

cd $HOME/PHARE
. .venv/bin/activate

export PYTHONPATH="${WORK}/build:${PWD}:${PWD}/pyphare"
cd $CWD
srun --ntasks=80 --ntasks-per-node=40 --cpus-per-task=1 -- python3 config.py
