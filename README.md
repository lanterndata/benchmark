Setup

- Add id_rsa to root to support Github connection
- Check db/init to see DB setup.
- Check db/scripts for scripts to install / update lantern / pgvector
- Download the data [here](http://corpus-texmex.irisa.fr/)
- Download the Python requirements with requirements.txt
- See experiments/scripts to see scripts to create the tables

Scripts you can run
- experiments/recall_experiment.py
- experiments/create_experiment.py
- experiments/select_experiment.py
- experiments/disk_usage_experiment.py


### Examples

Run recall experiments on Lantern
```bash
python  ./experiments/recall_experiment.py --dataset sift --extension pgvector --N 10k 100k
```

Use a custom database URL to run the experiments
```bash
DATABASE_URL='postgresql://ngalstyan:abra@localhost:5432/testdb' python  ./experiments/recall_experiment.py --dataset sift --extension pgvector --N 10k 100k
 ```
