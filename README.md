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
python3 -m scripts.setup
```

# Scripts you can run
- experiments/recall_experiment.py
- experiments/create_experiment.py
- experiments/select_experiment.py
- experiments/disk_usage_experiment.py