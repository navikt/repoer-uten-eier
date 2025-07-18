#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
# ]
# ///

from collections import Counter
from classes import Repository

import pathlib
import click


def load_repos() -> list[Repository]:
    data_dir = pathlib.Path(__file__).parent / "data"
    return [Repository.load(file) for file in data_dir.glob("*.json")]


@click.command()
@click.option("--num-authors", default=40, help="Number of top authors to consider")
def main(num_authors: int):
    repos = load_repos()
    unique_authors_per_repo = [
        set(commit.email for commit in repo.commits) for repo in repos
    ]
    all_unique_authors = [
        author for authors in unique_authors_per_repo for author in authors
    ]

    counter = Counter(all_unique_authors)

    top_authors = set(author for author, _ in counter.most_common()[:num_authors])

    total_repos = sum(
        1
        for repo in repos
        if any(commit.email in top_authors for commit in repo.commits)
    )
    print(
        f"Repositories with recent commits by top {num_authors:3d} authors: {total_repos:3d}"
    )


if __name__ == "__main__":
    main()
