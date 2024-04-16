from src.batching import batch_items
from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse
from tqdm.asyncio import tqdm_asyncio as asyncio


async def embed_data(data):
    async def embed_batch(batch):
        client = AsyncOpenAI()
        res: CreateEmbeddingResponse = await client.embeddings.create(
            # Clip to max of 6000 chars for now since max emebdding context is 8k
            input=[item["text"][:6000] for item in batch],
            model="text-embedding-3-small",
        )
        return [
            {"embedding": embedding.embedding, "item": item}
            for embedding, item in zip(res.data, batch)
        ]

    batches = batch_items(data)
    coros = [embed_batch(batch) for batch in batches]
    res = await asyncio.gather(*coros)
    return [item for sublist in res for item in sublist]
