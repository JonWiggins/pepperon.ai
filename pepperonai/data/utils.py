"""
Data Set Utils

**In progress - Incomplete **

This will be a collection of static methods to help manage a dataset

"""

__author__ = "Jon Wiggins"

import math
import numpy as np
import pandas as pd
import itertools
import random


def fowlkesmallowsindex(
    first_clustering: "Set[object]",
    second_clustering: "Set[object]",
    all_data_points: "Set[object]",
) -> float:
    """
    Given two clusterings and a list of all the points, calculates the Fowlkes-Mallows Index

    :param first_clustering: the first set of iterables to compare
    :param second_clustering: the second set of iterables to compare
    :param all_data_points: all of the datapoints in the two clusterings as an iterable

    :return: the Fowlkes Mallows Index as a float
    """

    # TP = the number of points that are present in the same cluster in both clusterings
    # FP = the number of points that are present in the same cluster in clustering1 but not clustering2
    # FN = the number of points that are present in the same cluster in clustering2 but not clustering1
    # TN = the number of points that are in different clusters in both clusterings
    TP = 0
    FP = 0
    FN = 0
    TN = 0

    for element in all_data_points:
        elements_first_location = None
        for cluster in first_clustering:
            if element in cluster:
                elements_first_location = cluster
                break

        elements_second_location = None
        for cluster in second_clustering:
            if element in cluster:
                elements_second_location = cluster
                break

        for comparison_element in all_data_points:
            comparisons_first_cluster = None
            for cluster in first_clustering:
                if comparison_element in cluster:
                    comparisons_first_cluster = cluster
            comparisons_second_cluster = None
            for cluster in second_clustering:
                if comparison_element in cluster:
                    comparisons_second_cluster = cluster

            if (
                elements_first_location == comparisons_first_cluster
                and elements_second_location == comparisons_second_cluster
            ):
                TP += 1
            elif (
                elements_first_location == comparisons_first_cluster
                and not elements_second_location == comparisons_second_cluster
            ):
                FP += 1
            elif (
                not elements_first_location == comparisons_first_cluster
                and elements_second_location == comparisons_second_cluster
            ):
                FN += 1
            elif (
                not elements_first_location == comparisons_first_cluster
                and not elements_second_location == comparisons_second_cluster
            ):
                TN += 1

    if TP + FP == 0 or TP + FN == 0:
        return 0

    return math.sqrt((TP / (TP + FP))) * (TP / (TP + FN))


def purity(first_clustering: "Set[object]", second_clustering: "Set[object]") -> float:
    """
    Returns the purity of the given two clusterings

    :param first_clusterings: a set of iterables to compare
    :param second_clusterings: a set of iterables to compare

    :return: the purity index as a float
    """
    summation = 0

    for cluster in first_clustering:
        highest = 0
        for comparer in second_clustering:
            next_element = len(cluster.intersection(comparer))
            if next_element > highest:
                highest = next_element

        summation += highest

    # find total number of data points
    N = sum(len(cluster) for cluster in first_clustering)

    if N == 0:
        return 0

    return summation / N


def jackknife(
    data: "dataframe",
    fold_count: int,
    save: bool,
    save_dir: str,
    experiment_id: str = "",
) -> "List[dataframe]":
    """
    Jackknifes the given dataframe into fold_count number of dataframes
    
    Randomly shuffles the dataframe before splitting
    Will also save the folds to a given directory

    :param data: a dataframe source
    :param fold_count: the number of folds to create
    :param save: if true, saves the folds to the given directory
    :param save_dir: a directory as a string on where to save the folds as a csv
    :param experiment_id: an identifier to use when saving the folds to idenfity them later

    :return: a list of dataframes
    """
    data = data.sample(frac=1)
    folds = np.array_split(data, fold_count)
    np.random.shuffle(folds)

    if save:
        for count, fold in enumerate(folds):
            fold.to_csv(save_dir + "fold" + str(count) + "_" + experiment_id + ".csv")

    return folds


def random_unit_vector(dimensions: int, seed: int = None) -> "List[float]":
    """
    Returns a random unit vector in the given number of dimensions
    Created using Gausian Random vars

    :param dimensions: desired dimensions
    :param seed: nullable, random var seed

    :return: random unit vecotor
    """
    raw = []
    magnitude = 0
    if seed:
        random.seed(seed)

    for count in range(dimensions):
        uniform1 = random.uniform(0, 1)
        uniform2 = random.uniform(0, 1)
        toadd = math.sqrt(-2 * math.log(uniform1)) * math.cos(2 * math.pi * uniform2)
        magnitude += toadd ** 2
        raw.append(toadd)

    magnitude = math.sqrt(magnitude)
    return [element / magnitude for element in raw]


def model_accuracy(
    model: "Model",
    probe_method: "function",
    test_set: "dataframe",
    test_answer: "List[object]",
) -> float:
    """
    Tests the model on the given set and returns the accuracy

    :param model: a trained model
    :param probe_method: the models query method, takes an instance as a parameter and returns the prediction
    :param test_set: an iterable object to probe with
    :param test_answer: an iterable object to correlate with the models predictions

    :return: the number of correct predicitons / total number of probes
    """
    correct_count = 0
    for index, element in enumerate(test_set):
        if model.probe_method(element) == test_answer[index]:
            correct_count += 1

    return correct_count / len(test_set)


def model_error(
    model: "Model",
    probe_method: "function",
    test_set: "dataframe",
    test_answer: "List[object]",
) -> float:
    """
    Tests the model on the given set and returns the error

    :param model: a trained model
    :param probe_method: the models query method, takes an instance as a parameter and returns the prediction
    :param test_set: an iterable object to probe with
    :param test_answer: an iterable object to correlate with the models predictions

    :return: 1- the number of correct predicitons / total number of probes
    """
    return 1 - model_accuracy(model, probe_method, test_set, test_answer)


def get_average_accuracy_and_sd(
    model: "Model", probe_method: "function", folds: "dataframe"
) -> "Tuple(float, float)":
    """
    *incomplete*
    
    Tests the given model on each fold
    """
    # TODO generalize this for all different models
    accs = []
    for test_fold in folds:
        if test_fold == folds[0]:
            train_set = folds[1]
        else:
            train_set = folds[0]
        for element in folds:
            if element == test_fold:
                continue
            train_set = train_set.append(element)
        # TODO generalize and train here
        accs.append(
            model_accuracy(
                model, probe_method, test_set=test_fold, test_answer=test_fold
            )
        )
    return np.mean(accs, axis=0), np.std(accs, axis=0)


def enumerate_hyperparameter_combinations(parameter_to_options: dict) -> "List[dict]":
    """
    Returns a list of dictionaries of all hyperparameter options

    :param parameter_to_options: a dictionary that maps parameter name to a list of possible values

    :return: a list of dictionaries that map parameter names to set values
    """
    keys, values = zip(*parameter_to_options.items())
    return [dict(zip(keys, v)) for v in itertools.product(*values)]


def grid_search(
    model_type: "Model",
    probe_method: "function",
    parameter_to_options: dict,
    train_set: "dataframe",
    train_answers: "List[object]",
    test_set: "dataframe",
    test_answers: "List[object]",
    fold_count: int,
    print_results: bool,
) -> "Tuple[Model, dict, float, float]":
    """
    *incomplete*
    
    Trains a model with every possible set of given hyperparameters and returns the best performing one

    :param model_type: a class of model to train
    :param probe_method: the method in model_type to probe after training
    :param parameter_to_options: a dictionary that maps each hyperparamer to a list of possible values
    :param train_set: a set of training input
    :param train_answers: a set of trianing set answers to correlate with train_set
    :param test_set: a set of testing input
    :param test_answers: a set of testing answers to correlate with test_answers
    :param fold_count: the number of jackknife folds to evaluate with
    :param print_results: prints the accuracy and standard deviation of each experiment if true
    
    :return: the model and info as; (the model, the hyperparameter dict, the average accuracy, the standard deviation)
    """

    best_params = None
    best_model = None
    best_acc = None
    best_std = None
    for parameter_set in enumerate_hyperparameter_combinations(parameter_to_options):
        # TODO generalize this for all different models
        current_model = model_type(**parameter_set)
        # TODO possibly move where training takes place
        current_model.train(train_set, train_answers)
        acc, sd = get_average_accuracy_and_sd(current_model, probe_method, fold_count)
        if print_results:
            print(type(model_type))
            print("Parameters:", parameter_set)
            print("Average Accuracy:", acc)
            print("Average Standard Deviation:", sd)
        if not best_acc or best_acc < acc:
            best_model = current_model
            best_params = parameter_set
            best_acc = acc
            best_std = sd

    return best_model, best_params, best_acc, best_std
