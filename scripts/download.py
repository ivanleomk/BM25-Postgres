from datasets import load_dataset
from tqdm import tqdm
from collections import defaultdict
import os
import json

selected_repos = set(
    [
        "facebook/react",
        "pytorch/pytorch",
    ]
)


def download_dataset(n=300):
    dataset = (
        load_dataset("bigcode/the-stack-github-issues", split="train", streaming=True)
        .filter(lambda row: row["repo"] in selected_repos)
        .take(n)
    )
    repos = defaultdict(int)
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/issues.jsonl")
    )
    with open(file_path, "a+") as f:
        for row in tqdm(dataset, total=n):
            for event in row["events"]:
                f.write(
                    json.dumps(
                        {
                            "repo": row["repo"],
                            "issue_id": row["issue_id"],
                            "issue_number": row["issue_number"],
                            "timestamp": event["datetime"],
                            "text": event["text"],
                            "context": row["content"],
                        }
                    )
                    + "\n"
                )
            repos[row["repo"]] += 1

    repo_names = list(repos.keys())
    repo_names.sort()

    print(f"Crawled {n} issues")
    for repo in repo_names:
        print(f"{repo}: {repos[repo]}")

    print(f"Total: {sum(repos.values())}")


if __name__ == "__main__":
    download_dataset(20)
