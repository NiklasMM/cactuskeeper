import sys

import click
from git import Repo

from cactuskeeper.git import get_bugfixes_for_branch, get_release_branches


@click.group()
def cli():
    pass


@cli.command()
@click.option('--repo', default=".", help="Path to the repository root")
def check(repo):
    cc_repo = Repo(repo)

    current_branch = cc_repo.active_branch
    release_branches = get_release_branches(cc_repo)

    branches_to_check = []
    for branch in reversed(release_branches):
        if current_branch == branch["branch"]:
            break
        else:
            branches_to_check.append(branch)

    clean = True
    for branch in branches_to_check:
        fixes = get_bugfixes_for_branch(
            cc_repo, branch["branch"], current_branch
        )

        if len(fixes) > 0:
            clean = False
            click.echo(
                "Branch '{other}' contains the following "
                "fixes not present in '{base}'".format(
                    base=current_branch, other=branch["branch"]
                )
            )
            for issue, shortlog in fixes.items():
                click.echo("\t {shortlog} {issue}".format(shortlog=shortlog, issue=issue))
    if clean:
        click.echo("The current branch is clean")
    else:
        click
        sys.exit(1)
