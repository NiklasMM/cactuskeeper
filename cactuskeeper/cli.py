import click
from git import Repo
import re
from itertools import takewhile

RELEASE_BRANCHES = re.compile(r"release/v(?P<major>\d+)\.(?P<minor>\d+)")


def get_release_branches(repo, release_branch_re=RELEASE_BRANCHES):
    release_branches = []

    for branch in repo.branches:
        m = release_branch_re.match(str(branch))
        if m:
            release_branches.append(
                (branch, (int(m.group("major")), int(m.group("minor"))))
            )

    return sorted(release_branches, key=lambda x: x[1], reverse=True)


def get_bugfixes_for_branch(repo, branch, base_branch):
    commits_on_branch = takewhile(
        lambda commit: commit not in repo.iter_commits(base_branch, max_count=100),
        repo.iter_commits(branch, max_count=10)
    )
    result = []
    for commit in commits_on_branch:
        if commit.message.startswith("release"):
            continue
        m = re.search("(#\d+)", commit.message)
        if m:
            result.append(m.group(0))
    return result


@click.command()
@click.option('--repo', default=".", help="Path to the repository root")
def cli(repo):
    cc_repo = Repo(repo)

    current_branch = cc_repo.active_branch
    branches = get_release_branches(cc_repo)

    get_bugfixes_for_branch(cc_repo, branches[1][0], current_branch)
