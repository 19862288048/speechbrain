#!/usr/bin/python
"""
Snippet to aggregate results based on four different EEG training paradigms
(within-session, cross-session, leave-one-session-out, leave-one-subject-out).

To run this script (e.g., exp_results: results/MOABB/EEGNet_BNCI2014001/<seed>; required metrics: ["acc", "loss", "f1"]):

    > python3 parse_results.py results/MOABB/EEGNet_BNCI2014001/1234 acc loss f1

Author
------
Francesco Paissan, 2021
"""

from pathlib import Path
from pickle import load
from typing import Tuple
from numpy import mean, std, round
import sys


def load_metrics(filepath: Path) -> dict:
    """Loads pickles and parses into a dictionary

    :param filepath: [description]
    :type filepath: Path
    :return: [description]
    :rtype: dict
    """

    try:
        with open(filepath, "rb") as f:
            temp = load(f)

        return temp
    except Exception as e:
        print(f"Error on {str(filepath)} - {str(e)}")
        return None


def visualize_results(paradigm: str, results: dict, vis_metrics: list) -> None:
    """Prints aggregated strings

    :param paradigm: [description]
    :type paradigm: str
    :param results: [description]
    :type results: dict
    :param vis_metrics: [description]
    :type vis_metrics: list
    """
    print("\n----", paradigm.name, "----")
    for key in results:
        if type(results[key]) == dict:
            for m in vis_metrics:
                print(
                    key,
                    m,
                    round(mean(results[key][m]), 4),
                    "±",
                    round(std(results[key][m]), 4),
                )
        else:
            if key in vis_metrics:
                print(
                    key,
                    round(mean(results[key]), 4),
                    "±",
                    round(std(results[key]), 4),
                )


def parse_one_session_out(
    paradigm: Path,
    vis_metrics: list = [],
    stat_metrics: list = ["loss", "f1", "acc"],
    metric_file: str = "test_metrics.pkl",
) -> dict:
    """Aggregates results obtain by helding back one session as test set and
    using the remaining ones to train the neural nets

    :param paradigm: [description]
    :type paradigm: Path
    :return: [description]
    :rtype: dict
    """
    folds = sorted(paradigm.iterdir())
    out_stat = {
        key.name: {metric: [] for metric in stat_metrics}
        for key in sorted(folds[0].iterdir())
    }

    for f in folds:
        child = sorted(f.iterdir())
        for sess in child:
            metrics = load_metrics(sess.joinpath(metric_file))
            if metrics is not None:
                for m in stat_metrics:
                    out_stat[sess.name][m].append(metrics[m])
            else:
                print("Something was wrong when computing ", paradigm)

    if len(vis_metrics) != 0:
        visualize_results(paradigm, out_stat, vis_metrics)

    return out_stat


def parse_cross_section(
    paradigm: Path,
    vis_metrics: list = [],
    stat_metrics: list = ["loss", "f1", "acc"],
    metric_file: str = "test_metrics.pkl",
) -> dict:
    """Aggregates results obtained using all session' signals merged together.
    Training and test sets are defined using a stratified cross-validation partitioning.

    :param paradigm: [description]
    :type paradigm: Path
    :return: [description]
    :rtype: dict
    """
    folds = sorted(paradigm.iterdir())
    out_stat = {metric: [] for metric in stat_metrics}

    for f in folds:
        child = sorted(f.iterdir())
        sess_metrics = {metric: [] for metric in stat_metrics}

        for sess in child:
            metrics = load_metrics(sess.joinpath(metric_file))
            if metrics is not None:
                for m in stat_metrics:
                    sess_metrics[m].append(metrics[m])

            else:
                print("Something was wrong when computing ", f)

        for m in stat_metrics:
            out_stat[m].append(mean(sess_metrics[m]))

    if len(vis_metrics) != 0:
        visualize_results(paradigm, out_stat, vis_metrics)

    return out_stat


def parse_one_sub_out(
    paradigm: Path,
    vis_metrics: list = [],
    stat_metrics: list = ["loss", "f1", "acc"],
    metric_file: str = "test_metrics.pkl",
) -> dict:
    """Aggregates results obtained helding out one subject
    as test set and using the remaining ones for training.

    :param paradigm: [description]
    :type paradigm: Path
    :return: [description]
    :rtype: dict
    """
    folds = sorted(paradigm.iterdir())
    out_stat = {metric: [] for metric in stat_metrics}

    for f in folds:
        metrics = load_metrics(f.joinpath(metric_file))
        if metrics is not None:
            for m in stat_metrics:
                out_stat[m].append(metrics[m])
        else:
            print("Something was wrong when computing ", f)

    if len(vis_metrics) != 0:
        visualize_results(paradigm, out_stat, vis_metrics)

    return out_stat


def parse_within_session(
    paradigm: Path,
    vis_metrics: list = [],
    stat_metrics: list = ["loss", "f1", "acc"],
    metric_file: str = "test_metrics.pkl",
) -> dict:
    """For each subject and for each session, the training
    and test sets were defined using a stratified cross-validation partitioning.

    :param paradigm: [description]
    :type paradigm: Path
    :return: [description]
    :rtype: dict
    """
    folds = sorted(paradigm.iterdir())
    out_stat = {
        key.name: {metric: [] for metric in stat_metrics}
        for key in sorted(folds[0].iterdir())
    }

    for f in folds:
        child = sorted(f.iterdir())
        for sess in child:
            sub_perf = {metric: [] for metric in stat_metrics}

            for sub in sess.iterdir():
                metrics = load_metrics(sub.joinpath(metric_file))
                if metrics is not None:
                    for m in stat_metrics:
                        sub_perf[m].append(metrics[m])
                else:
                    print("Something was wrong when computing ", f)

            for k in sub_perf.keys():
                out_stat[sess.name][k].append(mean(sub_perf[k]))

    if len(vis_metrics) != 0:
        visualize_results(paradigm, out_stat, vis_metrics)

    return out_stat


def aggregate_nested(
    results: dict,
    metric_file: str = "test_metrics.pkl",
    stat_metrics: list = ["loss", "f1", "acc"],
):
    temp = {key: [] for key in stat_metrics}
    for _, v in results.items():
        for k, r in v.items():
            temp[k].append(mean(r))

    return temp


def aggregate_single(
    results: dict,
    metric_file: str = "test_metrics.pkl",
    stat_metrics: list = ["loss", "f1", "acc"],
):
    temp = {key: [] for key in stat_metrics}
    for k, r in results.items():
        temp[k].append(mean(r))

    return temp


available_parsers = {
    "leave-one-session-out": parse_one_session_out,
    "cross-session": parse_cross_section,
    "leave-one-subject-out": parse_one_sub_out,
    "within-session": parse_within_session,
}

available_aggrs = {
    "leave-one-session-out": aggregate_nested,
    "within-session": aggregate_nested,
    "leave-one-subject-out": aggregate_single,
    "cross-session": aggregate_single,
}

def aggregate_metrics(
    verbose=1,
    metric_file="test_metrics.pkl",
    stat_metrics=["loss", "f1", "acc"],
) -> Tuple:
    """Parses results and computes statistics over all
    paradigms.

    :return: [mean and std on different paradigms]
    :rtype: [Tuple]
    """
    results_folder = Path(sys.argv[1])
    vis_metrics = stat_metrics

    available_paradigms = list(map(lambda x: x.stem, sorted(results_folder.iterdir())))
    overall_stat = {key: [] for key in stat_metrics}

    parsers = {k : available_parsers[k] for k in available_paradigms}
    aggr = {k : available_aggrs[k] for k in available_paradigms}

    for paradigm in sorted(results_folder.iterdir()):
        results = parsers[paradigm.name](
            paradigm,
            vis_metrics,
            stat_metrics=stat_metrics,
        )
        temp = aggr[paradigm.name](
            results, metric_file=metric_file, stat_metrics=stat_metrics
        )

        for k in temp.keys():
            overall_stat[k].extend(temp[k])

    for k in stat_metrics:
        overall_stat[k + "_std"] = std(overall_stat[k])
        overall_stat[k] = mean(overall_stat[k])

    return overall_stat


if __name__ == "__main__":
    stat_metrics = sys.argv[2:]
    temp = aggregate_metrics(
        verbose=1, metric_file="test_metrics.pkl", stat_metrics=stat_metrics
    )

    print("\nAggregated results")
    for k in stat_metrics:
        print(k, temp[k], "+-", temp[k + "_std"])
