
import math
import recall_experiment

def hyperparameter_search(extension, dataset, N):
    hyperparameters = []
    if extension == 'pgvector':
        sqrt_N = int(math.sqrt(N))
        lists_options = list(map(lambda p: int(p * sqrt_N), [0.6, 0.8, 1.0, 1.2, 1.4]))
        probes_options = [1, 2, 4, 8, 16, 32]
        hyperparameters = [{'lists': l, 'probes': p} for l in lists_options for p in probes_options]
    if extension == 'lantern':
        hyperparameters = []
    
    if len(hyperparameters) == 0:
        return None

    best_hyperparameters = None
    best_recall = 0
    for hyperparameter in hyperparameters:
        index_params = { 'hyperparameter': hyperparameter }
        recall = recall_experiment.generate_result(extension, dataset, N, [5], index_params=index_params)[0]
        if recall > best_recall:
            best_recall = recall
            best_hyperparameters = hyperparameter
    
    return best_hyperparameters
   


