def warn(*args, **kwargs):
    pass

import warnings
warnings.warn = warn # to ignore all warnings.

import pickle
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


# TODO: change to be like _data_main below, and make python module
# this answer https://stackoverflow.com/a/50474562 and others
import treeUtils

import loadModel

from random import seed
RANDOM_SEED = 54321
seed(RANDOM_SEED) # set the random seed so that the random permutations can be reproduced again
np.random.seed(RANDOM_SEED)

SIMPLIFY_TREES = False

def trainAndSaveModels(experiment_folder_name, model_class, dataset_string, X_train, X_test, y_train, y_test, feature_names):

    log_file = open(f'{experiment_folder_name}/log_training.txt','w')

    if model_class == 'tree':
        model_pretrain = DecisionTreeClassifier()
    elif model_class == 'forest':
        model_pretrain = RandomForestClassifier()
    elif model_class == 'lr':
        # IMPORTANT: The default solver changed from ‘liblinear’ to ‘lbfgs’ in 0.22. Results may differ slightly from paper.
        model_pretrain = LogisticRegression(penalty='l2') # default
    elif model_class == 'mlp':
        model_pretrain = MLPClassifier(hidden_layer_sizes = (10, 10))

    print('[INFO] Training `{}` on {:,} samples (%{:.2f} of {:,} samples)...'.format(model_class, X_train.shape[0], 100 * X_train.shape[0] / (X_train.shape[0] + X_test.shape[0]), X_train.shape[0] + X_test.shape[0]), file=log_file)
    model_trained = model_pretrain.fit(X_train, y_train)

    # OVERRIDE MODEL_TRAINED; to be used for test purposes against pytorch on
    # {mortgage, random, german, credit} x {lr, mlp}
    if model_class in {'lr', 'mlp'}:
        if dataset_string in {'mortgage', 'random', 'twomoon', 'german'}: # NOT credit as I don't want to ruin master
            model_trained = loadModel.loadModelForDataset(model_class, dataset_string)

    print('\tTraining accuracy: %{:.2f}'.format(accuracy_score(y_train, model_trained.predict(X_train)) * 100), file=log_file)
    print('\tTesting accuracy: %{:.2f}'.format(accuracy_score(y_test, model_trained.predict(X_test)) * 100), file=log_file)
    print('[INFO] done.\n', file=log_file)

    if model_class == 'tree':
        if SIMPLIFY_TREES:
            print('[INFO] Simplifying decision tree...', end = '', file=log_file)
            model_trained.tree_ = treeUtils.simplifyDecisionTree(model_trained, False)
            print('\tdone.', file=log_file)
        treeUtils.saveTreeVisualization(model_trained, model_class, '', X_test, feature_names, experiment_folder_name)
    elif model_class == 'forest':
        for tree_idx in range(len(model_trained.estimators_)):
            if SIMPLIFY_TREES:
                print(f'[INFO] Simplifying decision tree (#{tree_idx + 1}/{len(model_trained.estimators_)})...', end = '', file=log_file)
                model_trained.estimators_[tree_idx].tree_ = treeUtils.simplifyDecisionTree(model_trained.estimators_[tree_idx], False)
                print('\tdone.', file=log_file)
            treeUtils.saveTreeVisualization(model_trained.estimators_[tree_idx], model_class, f'tree{tree_idx}', X_test, feature_names, experiment_folder_name)

    pickle.dump(model_trained, open(f'{experiment_folder_name}/_model_trained', 'wb'))
    return model_trained

