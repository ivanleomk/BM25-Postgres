from typing import Callable, List


def calculate_recall(chunk_id, predictions):
    return 0 if chunk_id not in predictions else 1


def calculate_mrr(chunk_id, predictions):
    return 0 if chunk_id not in predictions else 1 / (predictions.index(chunk_id) + 1)


def slice_predictions_at_k(k: int, score: Callable[[str, List[str]], float]):
    def wrapper(chunk_id: str, predictions: List[str]):
        return score(chunk_id, predictions[:k])

    return wrapper
