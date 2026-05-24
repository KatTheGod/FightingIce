#!/bin/bash
#SBATCH -p bigbatch
#SBATCH -J cull
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

PROJECT_DIR="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
EMPTY_DIR="/tmp/empty_dir_$$"

# Create a temporary empty directory
mkdir -p "$EMPTY_DIR"

# List of directories to clean
targets=(
    "$PROJECT_DIR/err"
    "$PROJECT_DIR/out"
    "$PROJECT_DIR/log/engines"
    "$PROJECT_DIR/log/frameData"
    "$PROJECT_DIR/log/motions"
    "$PROJECT_DIR/log/point"
    "$PROJECT_DIR/log/replay"
    "$PROJECT_DIR/log/sound"
    "$PROJECT_DIR/custom_motions"
    "$PROJECT_DIR/dask_logs"
    "$PROJECT_DIR/dask_schedulers"
    "$PROJECT_DIR/solution_explorer/logs"
)

echo "Starting cleanup in $PROJECT_DIR..."

for dir in "${targets[@]}"; do
    if [ -d "$dir" ]; then
        echo "Clearing: $dir"
        rsync -a --delete "$EMPTY_DIR/" "$dir/"
    else
        echo "Skipping (not found): $dir"
    fi
done

# Cleanup
rmdir "$EMPTY_DIR"
echo "Cleanup complete."