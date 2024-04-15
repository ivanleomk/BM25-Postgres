def batch(data, batch_size=20):
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
