import datetime
from dataclasses import dataclass
import json
import pathlib
from typing import Self


@dataclass(frozen=True)
class Commit:
    email: str
    date: datetime.date


@dataclass
class Repository:
    name: str
    full_name: str
    last_push: datetime.date
    commits: list[Commit] | None = None

    def __hash__(self):
        return hash(self.name)

    def __gt__(self, other) -> bool:
        return self.name > other.name

    def dump(self) -> dict:
        return {
            "name": self.name,
            "full_name": self.full_name,
            "last_push": self.last_push.isoformat(),
            "commits": [
                {"email": commit.email, "date": commit.date.isoformat()}
                for commit in (self.commits or [])
            ],
        }

    @classmethod
    def load(cls, path: pathlib.Path) -> Self:
        data = json.loads(path.read_bytes())
        return Repository(
            name=data["name"],
            full_name=data["full_name"],
            last_push=datetime.datetime.strptime(data["last_push"], "%Y-%m-%d").date(),
            commits=[
                Commit(
                    email=commit["email"],
                    date=datetime.datetime.strptime(commit["date"], "%Y-%m-%d").date(),
                )
                for commit in data.get("commits", [])
            ],
        )
