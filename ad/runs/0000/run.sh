#!/usr/bin/env bash

## BEGIN SBATCH directives
#SBATCH --job-name=0000
#SBATCH --output=0000.txt
#SBATCH --constraint=GENOA
#SBATCH --nodes=1
#SBATCH --ntasks=192
#SBATCH --ntasks-per-node=192
#SBATCH --threads-per-core=1 # --hint=nomultithread
#SBATCH --time=24:00:00
#SBATCH --account=c1715704
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=philip.deegan@lpp.polytechnique.fr
##SBATCH --partition=genoa
## END SBATCH directives

# Adastra SLURM info
# https://dci.dci-gitlab.cines.fr/webextranet/user_support/index.html#batch-scripts

set -exu
set -o pipefail

module load cray-python/3.11.5 gcc-native/12.1 cray-hdf5-parallel

CWD="/lus/home/CT4/c1715704/pdeegan/work/skale/runs/0000"

cd "$HOME/PHARE"
[ ! -f ".venv/bin/activate" ] && echo "error: venv not found" && exit 1

# shellcheck disable=SC1091
. .venv/bin/activate
export PYTHONPATH="${WORKDIR}/build:${PWD}:${PWD}/pyphare"

cd "$CWD"
srun --ntasks=192 --ntasks-per-node=192 --cpus-per-task=1 -- python3 -uO "$CWD/config.py"
