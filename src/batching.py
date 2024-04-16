from typing import List, TypeVar

T = TypeVar("T")


def batch_items(data: List[T], batch_size: int = 20) -> List[List[T]]:
    """
    Batch a list of type T into type List[List[T]] given a batch size
    """
    batch = []

    for item in data:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch
