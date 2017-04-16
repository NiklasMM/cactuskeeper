import re
from itertools import takewhile
from distutils.version import StrictVersion

RELEASE_BRANCHES = re.compile(r"release/v(?P<version>\d+\.\d+(\.\d+)?)")


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
            lambda commit: commit not in repo.iter_commits(base_branch, max_count=100),
            repo.iter_commits(branch, max_count=10)
        )
    else:
        commits_on_branch = repo.iter_commits(branch)

    result = []
    for commit in commits_on_branch:
        if commit.message.startswith("release"):
            continue
        m = re.search("(#\d+)", commit.message)
        if m:
            result.append(m.group(0))
    return result
