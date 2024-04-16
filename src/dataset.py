from tqdm import tqdm
from datasets import load_dataset
import hashlib


def fetch_dataset_rows(n: int, selected_repos: set[str]) -> list[dict[str, str]]:
    total_fetched_rows = int(n * 1.2)
    dataset = (
        load_dataset("bigcode/the-stack-github-issues", split="train", streaming=True)
        .filter(lambda row: row["repo"] in selected_repos)
        .take(total_fetched_rows)
    )
    items = []

    for row in tqdm(dataset, total=total_fetched_rows):
        for comment in row["events"]:
            # We don't process comments that are empty strings
            if not comment["text"]:
                continue
            item = {
                "repo": row["repo"],
                "issue_id": row["issue_id"],
                "issue_number": row["issue_number"],
                "timestamp": comment["datetime"],
                "text": comment["text"],
                "context": row["content"],
                "chunk_id": hashlib.md5(
                    f"{row['repo']}-{row['issue_id']}-{comment['text']}".encode("utf-8")
                ).hexdigest(),
            }
            items.append(item)

    return items
