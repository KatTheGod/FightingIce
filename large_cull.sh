#!/bin/bash
#SBATCH -p bigbatch
#SBATCH -J cull
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

PROJECT_DIR="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
OUTPUT_DIR="$PROJECT_DIR/cull_output"
OUTPUT_FILE="$OUTPUT_DIR/cull.txt"

mkdir -p "$OUTPUT_DIR"

# Mirror all output to cull_output/cull.txt as well as the slurm out file
exec > >(tee -a "$OUTPUT_FILE") 2>&1

targets=(
    # "$PROJECT_DIR/err"
    # "$PROJECT_DIR/out"
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

# Prints a heartbeat every 5 seconds until the directory disappears
monitor_progress() {
    local dir="$1"
    local label="$2"
    while [ -d "$dir" ]; do
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "[$(date '+%H:%M:%S')] deleting $label — $size remaining"
        sleep 5
    done
    echo "[$(date '+%H:%M:%S')] done: $label"
}

echo "=== Cleanup started at $(date) ==="

# Delete any orphaned _old_* directories left by previously killed cull jobs
echo "[$(date '+%H:%M:%S')] Scanning for orphaned _old_* directories..."
while IFS= read -r orphan; do
    label=$(basename "$orphan")
    echo "[$(date '+%H:%M:%S')] Removing orphan: $orphan"
    monitor_progress "$orphan" "$label" &
    (
        find "$orphan" -mindepth 1 -maxdepth 1 -type d | xargs -P 12 -r rm -rf
        rm -rf "$orphan"
    ) &
done < <(find "$PROJECT_DIR" -maxdepth 4 -type d -name '*_old_*' 2>/dev/null)
wait
echo "[$(date '+%H:%M:%S')] Orphan sweep complete."

for dir in "${targets[@]}"; do
    if [ -d "$dir" ]; then
        label=$(basename "$dir")
        old="${dir}_old_$$"

        echo "[$(date '+%H:%M:%S')] Clearing: $dir"
        mv "$dir" "$old"
        mkdir -p "$dir"

        monitor_progress "$old" "$label" &
        (
            find "$old" -mindepth 1 -maxdepth 1 -type d | xargs -P 12 -r rm -rf
            rm -rf "$old"
        ) &
    else
        echo "[$(date '+%H:%M:%S')] Skipping (not found): $dir"
    fi
done

wait
echo "=== Cleanup complete at $(date) ==="
