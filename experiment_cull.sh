#!/bin/bash
#SBATCH -p batch
#SBATCH -J cull_rgx
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

# Regex applied to the full file path. Only matching files are deleted.
# Example: "ZEN.*\.json$" deletes all ZEN character json files
experiment_regex="3_ex_cb_uq_mse_energy.*"
PROJECT_DIR="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"

targets=(
    "$PROJECT_DIR/log/engines"
    "$PROJECT_DIR/log/frameData"
    "$PROJECT_DIR/log/motions"
    "$PROJECT_DIR/log/point"
    "$PROJECT_DIR/log/replay"
    "$PROJECT_DIR/log/sound"
    "$PROJECT_DIR/custom_motions"
)

# NFS is I/O bound, not CPU bound — use more workers than cores to overlap round-trips
WORKERS=50

echo "=== experiment_cull started at $(date) ==="
echo "regex: $experiment_regex"

for dir in "${targets[@]}"; do
    echo "[$(date '+%H:%M:%S')] Scanning: $dir"
    find "$dir" -type f \
        | grep -E "$experiment_regex" \
        | xargs -P "$WORKERS" -r rm
    echo "[$(date '+%H:%M:%S')] Done: $dir"
done

echo "=== experiment_cull complete at $(date) ==="
