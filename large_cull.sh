#!/bin/bash
#SBATCH -p bigbatch
#SBATCH -J cull
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

PROJECT_DIR="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"

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

echo "Starting cleanup..."

for dir in "${targets[@]}"; do
    if [ -d "$dir" ]; then
        echo "Clearing: $dir"
        # Rename immediately so the directory appears empty at once
        mv "$dir" "${dir}_old_$$"
        mkdir -p "$dir"
        # Delete old contents using parallel workers on subdirs, fall back to find
        if find "${dir}_old_$$" -mindepth 1 -maxdepth 1 -type d | grep -q .; then
            find "${dir}_old_$$" -mindepth 1 -maxdepth 1 -type d \
                | xargs -P 12 rm -rf
        fi
        rm -rf "${dir}_old_$$" &
    else
        echo "Skipping (not found): $dir"
    fi
done

wait
echo "Cleanup complete."
