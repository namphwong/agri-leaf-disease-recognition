"""Classification metrics with explicit fixed-class and zero-division rules."""

import math


def classification_metrics(matrix: list[list[int]], labels: list[str]) -> dict:
    n = len(labels)
    if not n or len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("Confusion matrix shape must match labels")
    if any(type(value) is not int or value < 0 for row in matrix for value in row):
        raise ValueError("Confusion matrix must contain non-negative integers")
    total = sum(map(sum, matrix))
    if not total:
        raise ValueError("Evaluation set is empty")
    per_class = []
    for index, label in enumerate(labels):
        true_positive = matrix[index][index]
        support = sum(matrix[index])
        predicted = sum(row[index] for row in matrix)
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class.append(dict(label=label, precision=precision, recall=recall, f1=f1,
                              support=support, predicted=predicted))
    return {
        "accuracy": sum(matrix[i][i] for i in range(n)) / total,
        "macro_precision": math.fsum(row["precision"] for row in per_class) / n,
        "macro_recall": math.fsum(row["recall"] for row in per_class) / n,
        "macro_f1": math.fsum(row["f1"] for row in per_class) / n,
        "weighted_f1": math.fsum(row["f1"] * row["support"] for row in per_class) / total,
        "sample_count": total, "per_class": per_class,
        "zero_division": 0, "macro_class_count": n,
    }
