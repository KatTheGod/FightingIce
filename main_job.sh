#!/bin/bash
#SBATCH -p stampede
#SBATCH -c 15
#SBATCH -N 1
#SBATCH -J rerun
#SBATCH --ntasks-per-node=1
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

export PYTHONUNBUFFERED=1

mkdir -p dask_logs
mkdir -p dask_logs/worker_logs_$SLURM_JOB_ID
mkdir -p dask_schedulers

PROJECT_ROOT="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

NODES=1
CORES=15
BASE_PATH="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
DASK_FILE="${BASE_PATH}/dask_schedulers/dask_${SLURM_JOB_ID}.json"

conda run -n fightingIceEnv_stable dask scheduler \
        --scheduler-file $DASK_FILE \
        --port 0 \
        > dask_logs/scheduler_$SLURM_JOB_ID 2>&1 &
echo "Waiting for scheduler to write $DASK_FILE..."
until [ -f "$DASK_FILE" ]; do
     sleep 0.5
done
echo "Scheduler is online."

# We set quiet to silence the valid termination of srun
srun --quiet \
    --unbuffered \
    --output=dask_logs/worker_logs_$SLURM_JOB_ID/worker_%j_%t.out \
    --error=dask_logs/worker_logs_$SLURM_JOB_ID/worker_%j_%t.err \
    conda run --no-capture-output -n fightingIceEnv_stable dask worker \
    --scheduler-file $DASK_FILE \
    --nthreads $CORES \
    --resources "cores=$CORES" &

conda run -n fightingIceEnv_stable python main.py -sf $DASK_FILE -n $NODES -c $CORES -bp $BASE_PATH