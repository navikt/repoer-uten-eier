#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "google-cloud-bigquery",
# ]
# ///

import datetime
import json
import pathlib
import subprocess

from google.cloud import bigquery

from classes import Commit, Repository

MAX_REPOS = 1000
MAX_COMMITS = 100
DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def get_repos_without_owner() -> list[Repository]:
    client = bigquery.Client()
    query = """--sql
        select
            repositoryName,
            owners,
            lastPush
        from `appsec-prod-624d.appsec.github_repo_stats`
        where date(when_collected) >= current_date - interval 1 day
        and isArchived = false
        and array_length(owners) = 0
        qualify row_number() over (partition by repositoryName order by when_collected desc) = 1
        order by lastPush desc        
    """
    result = client.query(query).result()
    if result.total_rows == 0:
        print("Ingen repoer uten eiere funnet.")
        return []
    print(f"Fant {result.total_rows} repoer uten eiere.")
    repos = []
    for row in result:
        if not row.owners:
            repos.append(
                Repository(
                    name=row["repositoryName"],
                    full_name=f"navikt/{row['repositoryName']}",
                    last_push=row["lastPush"],
                )
            )
    return repos


def get_commits(owner: str, repo: str) -> list[Commit] | None:
    gh_command = f"gh api /repos/{owner}/{repo}/commits"
    try:
        output = subprocess.check_output(gh_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Feil ved henting av commits for {owner}/{repo}: {e}")
        return
    data = json.loads(output)
    try:
        return [
            Commit(
                email=commit["commit"]["author"]["email"],
                date=datetime.datetime.fromisoformat(
                    commit["commit"]["author"]["date"]
                ).date(),
            )
            for commit in data[:MAX_COMMITS]
            if "bot" not in commit["commit"]["author"]["name"].lower()
        ]
    except KeyError:
        print(
            f"Feil ved henting av commits for {owner}/{repo}. Sjekk at repoet eksisterer."
        )
        return []


def main():
    ownerless = get_repos_without_owner()
    for repo in ownerless[:MAX_REPOS]:
        if pathlib.Path(DATA_DIR / f"{repo.name}.json").exists():
            print(f"Repo {repo.name} finnes allerede")
            continue
        print(f"https://github.com/{repo.full_name} - Siste push: {repo.last_push}")
        commits = get_commits("navikt", repo.name)
        repo.commits = commits
        with open(f"{DATA_DIR}/{repo.name}.json", "w") as f:
            json.dump(repo.dump(), f, indent=2)


if __name__ == "__main__":
    main()
