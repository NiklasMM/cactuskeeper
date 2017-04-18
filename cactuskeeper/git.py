from distutils.version import StrictVersion
from itertools import takewhile
import re

RELEASE_BRANCHES = re.compile(r"release/v(?P<version>\d+\.\d+(\.\d+)?)")

COMMIT_REGEX = re.compile(r"^(?P<shortlog>.+)(\n|.)*(?P<issue>#\d+)")


def get_release_branches(repo, release_branch_re=RELEASE_BRANCHES):
    release_branches = []

    for branch in repo.branches:
        m = release_branch_re.match(str(branch))
        if m:
            version = StrictVersion(m.group("version"))
            release_branches.append({
                "version": version,
                "branch": branch
            })

    return sorted(release_branches, key=lambda x: x["version"], reverse=True)


def get_bugfixes_for_branch(repo, branch, base_branch=None):
    if base_branch is not None:
        commits_on_branch = takewhile(
            lambda commit: commit not in repo.iter_commits(base_branch),
            repo.iter_commits(branch)
        )
    else:
        commits_on_branch = repo.iter_commits(branch)

    result = {}
    for commit in commits_on_branch:
        if commit.message.startswith("release"):
            continue
        m = COMMIT_REGEX.match(commit.message)
        if m:
            result[m.group("issue")] = m.group("shortlog").strip()
    return result
