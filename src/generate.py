from typing import List
from src.models import (
    CommentChunk,
    QuestionAnswerPair,
    SyntheticDataQuestion,
    Keywords,
    KeywordGenerationResult,
)
from tqdm.asyncio import tqdm_asyncio as asyncio
from tenacity import retry, stop_after_attempt, wait_fixed
import instructor
from openai import AsyncOpenAI


async def generate_synthethic_questions(
    chunks: List[CommentChunk],
) -> List[SyntheticDataQuestion]:
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(30))
    async def generate_question(chunk: CommentChunk):
        client = instructor.from_openai(AsyncOpenAI())
        res: QuestionAnswerPair = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a world class algorithm that excels at generating great questions that can be only answered by a specific text that will soon be passed to you.",
                },
                {
                    "role": "assistant",
                    "content": f"Generate a question and answer pair that uses information and content that is specific to the following text chunk, including a chain of thought:\n\n{chunk.text[:10000]}",
                },
            ],
            response_model=QuestionAnswerPair,
            max_retries=3,
        )
        return SyntheticDataQuestion(question=res, source=chunk)

    coros = [generate_question(chunk) for chunk in chunks]
    res = await asyncio.gather(*coros)
    return res


async def generate_keywords_for_question_batch(
    questions: List[SyntheticDataQuestion],
) -> List[KeywordGenerationResult]:
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(30))
    async def generate_keywords(question: SyntheticDataQuestion):
        client = instructor.from_openai(AsyncOpenAI())
        res: Keywords = await client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "system",
                    "content": "You are a world class algorithm that excels at generating relevant keywords to questions. You are about to be passed a question to generate keywords for. ",
                },
                {
                    "role": "assistant",
                    "content": f"Here is the question: {question.question.question}. Make sure to generate at least 3 different keywords. Make sure to extract as many keywords from the question first before starting to generate your own.",
                },
            ],
            response_model=Keywords,
            max_retries=3,
        )
        return KeywordGenerationResult(keywords=res, question=question)

    coros = [generate_keywords(chunk) for chunk in questions]
    res = await asyncio.gather(*coros)
    return res
