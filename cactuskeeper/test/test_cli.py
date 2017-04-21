from click.testing import CliRunner
import mock
import pytest

from cactuskeeper.cli import cli
from cactuskeeper.test.helpers import MockRepo


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0


class TestCheck:
    def test_check_master_clean(self):
        """ master is clean if no release branch holds fixes not in master """
        repo = MockRepo(branches=["master", "release/v0.9"])

        repo.add_commit("release/v0.9", "release: v0.9", sha=1)

        repo.add_existing_commit("master", 1)

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            runner = CliRunner()
            result = runner.invoke(cli, ["check"])
            assert result.exit_code == 0
            assert "The current branch is clean" in result.output

    def test_check_release_clean(self):
        """
            release branches are clean if no earlier releases hold fixes
            not in this release
        """
        repo = MockRepo(branches=["master", "release/v0.9", "release/v0.8"])

        repo.add_commit("release/v0.9", "fix: bla \n blubi #123")
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
            assert "#123\tfix: bla" in result.output

            repo._active_branch = "release/v0.8"

            result = runner.invoke(cli, ["check"])
            # release/v0.8 is clean
            assert result.exit_code == 0


class TestRelease:

    @pytest.fixture(autouse=True)
    def setup_mock_repo(self):
        repo = MockRepo(branches=["master"])

        repo.add_commits("master", [
            "fix: something2 \n #2", "fix: something1 \n #1",
            "release: v1.2.3 \n info", "fix: something0 \n #0"
        ])

        repo.add_commit("master", "base", sha="12345")

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            yield

    def test_release_no_custom_base(self):
            runner = CliRunner()
            result = runner.invoke(cli, ["release"], input="n\n")

            assert result.exit_code == 0
            assert "The last release on the branch is 1.2.3." in result.output

            assert "fix: something2" in result.output
            assert "fix: something1" in result.output

            assert "fix: something0" not in result.output

    def test_release_custom_base(self):
            runner = CliRunner()
            result = runner.invoke(cli, ["release"], input="y\n12345\nn\n")

            assert result.exit_code == 0
            assert "The last release on the branch is 1.2.3." in result.output

            assert "fix: something2" in result.output
            assert "fix: something1" in result.output
            assert "fix: something0" in result.output
            assert "The specified commit was not found." not in result.output

    def test_release_custom_base_not_found(self):
            runner = CliRunner()
            result = runner.invoke(cli, ["release"], input="y\nidonotexist\n12345\nn\n")

            assert result.exit_code == 0
            assert "The last release on the branch is 1.2.3." in result.output

            assert "fix: something2" in result.output
            assert "fix: something1" in result.output
            assert "fix: something0" in result.output
            assert "The specified commit was not found." in result.output
