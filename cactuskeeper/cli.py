import click
from git import Repo

from cactuskeeper.git import get_release_branches, get_bugfixes_for_branch


@click.command()
@click.option('--repo', default=".", help="Path to the repository root")
def cli(repo):
    cc_repo = Repo(repo)

    current_branch = cc_repo.active_branch
    branches = get_release_branches(cc_repo)

    get_bugfixes_for_branch(cc_repo, branches[1][0], current_branch)
