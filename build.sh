#!/bin/sh

set -e

docker build -f environment/Dockerfile -t geffenlab/ecephys-phy-export:local .

mkdir -p $PWD/results
docker run --rm \
  --volume /home/ninjaben/codin/geffen-lab-data/processed_data/BH/AS20-minimal3/03112025:/home/ninjaben/codin/geffen-lab-data/processed_data/BH/AS20-minimal3/03112025 \
  --volume /home/ninjaben/codin/geffen-lab-data/raw_data/BH/AS20-minimal3/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0:/home/ninjaben/codin/geffen-lab-data/raw_data/BH/AS20-minimal3/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0 \
  --volume $PWD/results:$PWD/results \
  geffenlab/ecephys-phy-export:local \
  conda_run python /opt/code/run.py \
  --processed-data-dir /home/ninjaben/codin/geffen-lab-data/processed_data/BH/AS20-minimal3/03112025 \
  --ecephys-dir /home/ninjaben/codin/geffen-lab-data/raw_data/BH/AS20-minimal3/03112025/ecephys/AS20_03112025_trainingSingle6Tone2024_Snk3.1_g0 \
  --results-dir $PWD/results \
  --compute-pc-features false
