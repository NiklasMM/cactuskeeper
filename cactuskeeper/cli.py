import click
from git import Repo

from cactuskeeper.git import get_release_branches, get_bugfixes_for_branch


@click.group()
def cli():
    pass


@cli.command()
@click.option('--repo', default=".", help="Path to the repository root")
def check(repo):
    cc_repo = Repo(repo)

    current_branch = cc_repo.active_branch

    for release_branch in get_release_branches(cc_repo):
        get_bugfixes_for_branch(cc_repo, release_branch["branch"], current_branch)

    click.echo("The current branch is clean")
