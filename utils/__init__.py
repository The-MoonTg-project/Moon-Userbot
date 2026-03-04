#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sys import version_info

from dulwich import porcelain
from dulwich.errors import NotGitRepository
from dulwich.objects import Tag
from dulwich.refs import Ref
from dulwich.repo import Repo

from .db import db


def get_commits_since_latest_tag(repo):
    tags = list(repo.refs.subkeys(b"refs/tags/"))
    if not tags:
        return []

    latest_tag = sorted(tags)[-1]
    tag_sha = repo.refs[b"refs/tags/" + latest_tag]
    tag_obj = repo.get_object(tag_sha)

    target_commit_sha = tag_obj.object[1] if isinstance(tag_obj, Tag) else tag_obj.id

    commits = []
    for entry in repo.get_walker(include=[repo.head()]):
        if entry.commit.id == target_commit_sha:
            break
        commits.append(entry.commit)

    return commits


try:
    gitrepo = Repo(".")
except NotGitRepository:
    gitrepo = Repo.init(".")
    config = gitrepo.get_config()
    config.set(
        (b"remote", b"origin"),
        b"url",
        b"https://github.com/The-MoonTg-project/Moon-Userbot",
    )
    config.set((b"remote", b"origin"), b"fetch", b"+refs/heads/*:refs/remotes/origin/*")
    config.write_to_path()

    porcelain.fetch(gitrepo, b"origin")

    gitrepo.refs[Ref(b"refs/heads/main")] = gitrepo.refs[
        Ref(b"refs/remotes/origin/main")
    ]
    gitrepo.refs.set_symbolic_ref(Ref(b"HEAD"), Ref(b"refs/heads/main"))
    porcelain.reset(gitrepo, "hard")

commits_since_tag = get_commits_since_latest_tag(gitrepo)
userbot_version = f"2.5.{len(commits_since_tag)}"

modules_help = {}
requirements_list = []

python_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"

prefix = db.get("core.main", "prefix", ".")

__all__ = [
    "modules_help",
    "requirements_list",
    "python_version",
    "prefix",
    "gitrepo",
    "userbot_version",
]
