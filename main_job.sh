#!/bin/bash
#SBATCH -p stampede
#SBATCH -c 16
#SBATCH -N 5
#SBATCH -J mse_pw4
#SBATCH --ntasks-per-node=1
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

export PYTHONUNBUFFERED=1

mkdir -p dask_logs
mkdir -p dask_logs/worker_logs_$SLURM_JOB_ID
mkdir -p dask_schedulers

PROJECT_ROOT="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

N_GEN=10
GEN_PERIOD=6
META_SPACE_INDEX=15
ENGINE_MULTIPLIER=5
NO_MATCHES=6
N_PARTITIONS=7 # Don't change me often
N_NEIGHBORS=8 # Don't change me often
EXPERIMENT_NAME="mse_pairwise_4" # NB!!
PARTITION="stampede"
NODES=5
CORES=16

# Computing nthreads
THREADS_PER_WORKER=$(( (CORES / (ENGINE_MULTIPLIER * 3)) > 0 ? (CORES / (ENGINE_MULTIPLIER * 3)) : 1 ))

BASE_PATH="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
DASK_FILE="${BASE_PATH}/dask_schedulers/dask_${SLURM_JOB_ID}.json"

DASK_DISTRIBUTED__SCHEDULER__WORKER_SATURATION=1.0 \
conda run -n FI_3_12_13 dask scheduler \
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
    conda run --no-capture-output -n FI_3_12_13 dask worker \
    --scheduler-file $DASK_FILE \
    --nthreads $THREADS_PER_WORKER \
    --resources "cores=$CORES" \
    --no-nanny &

# conda run -n FI_3_12_13 python experiments/round_robin.py -sf $DASK_FILE -n $NODES -c $CORES -bp $BASE_PATH
conda run -n FI_3_12_13 python main.py \
    -sf $DASK_FILE -n $NODES -c $CORES -bp $BASE_PATH -p $PARTITION \
    --experiment_name $EXPERIMENT_NAME \
    --n_gen $N_GEN \
    --gen_period $GEN_PERIOD \
    --meta_space_index $META_SPACE_INDEX \
    --engine_multiplier $ENGINE_MULTIPLIER \
    --no_matches $NO_MATCHES \
    --n_partitions $N_PARTITIONS \
    --n_neighbors $N_NEIGHBORS