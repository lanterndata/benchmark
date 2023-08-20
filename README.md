# Setup
1. Install CMake
```
sudo apt update
sudo apt install build-essential
```
2. Install Docker: https://docs.docker.com/engine/install/debian/

3. Setup tables
```
sudo make build
sudo make up &
cd experiments
python3 -m scripts.setup_tables
```

# Overview
- Check db/init to see DB setup.
- Check db/scripts for scripts to install / update lantern / pgvector
- Download the data [here](http://corpus-texmex.irisa.fr/)
- Download the Python requirements with requirements.txt
- See experiments/scripts to see scripts to create the tables

# Scripts you can run
- experiments/recall_experiment.py
- experiments/create_experiment.py
- experiments/select_experiment.py
- experiments/disk_usage_experiment.py