import mock

from click.testing import CliRunner
from cactuskeeper.cli import cli

from cactuskeeper.test.helpers import MockRepo


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0


def test_check_master_clean():
    """ master is clean if no release branch holds fixes not in master """
    repo = MockRepo(branches=["master", "release/v0.9"])

    repo.add_commit("release/v0.9", "release: v0.9", sha=1)

    repo.add_existing_commit("master", 1)

    with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
        runner = CliRunner()
        result = runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "The current branch is clean" in result.output


def test_check_release_clean():
    """
        release branches are clean if no earlier releases hold fixes
        not in this release
    """
    repo = MockRepo(branches=["master", "release/v0.9", "release/v0.8"])

    repo.add_commit("release/v0.9", "fix: bla #123")
    repo.add_commit("release/v0.9", "release: v0.9", sha=1)
    repo.add_commit("release/v0.8", "release: v0.8", sha=0)

    repo.add_existing_commit("release/v0.8", 0)

    repo.add_existing_commit("master", 0)
    repo.add_existing_commit("master", 1)

    with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
        runner = CliRunner()

        result = runner.invoke(cli, ["check"])
        # master is not clean
        assert result.exit_code == 1
        assert "release/v0.9" in result.output
        assert "#123" in result.output

        repo._active_branch = "release/v0.8"

        result = runner.invoke(cli, ["check"])
        # release/v0.8 is clean
        assert result.exit_code == 0
