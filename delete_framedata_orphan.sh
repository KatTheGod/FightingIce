#!/bin/bash
#SBATCH -p batch
#SBATCH -J cull_r
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

SRC="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce/log/frameData_old_1805997_old_1734752"
DEST="/home-mscluster/kkungoane/large_cull_delete"

# echo "[$(date '+%H:%M:%S')] Moving $SRC -> $DEST"
# mv "$SRC" "$DEST"
# echo "[$(date '+%H:%M:%S')] Move complete. Starting deletion."

find "$DEST" -mindepth 1 -maxdepth 1 | xargs -P 12 -r rm -rf
rm -rf "$DEST"

echo "[$(date '+%H:%M:%S')] Done."
