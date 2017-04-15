import mock

from click.testing import CliRunner
from cactuskeeper.cli import cli

from cactuskeeper.test.helpers import MockRepo


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0


def test_check_clean():
    repo = MockRepo(branches=["master", "release/v0.9"])

    repo.add_commit("release/v0.9", "release: v0.9", sha=1)

    repo.add_existing_commit("master", 1)

    with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
        runner = CliRunner()
        result = runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "The current branch is clean" in result.output
