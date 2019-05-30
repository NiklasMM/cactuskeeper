from click.testing import CliRunner
import mock
import pytest

from cactuskeeper.cli import cli
from cactuskeeper.test.helpers import MockRepo, write_config_file


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0


def test_config_without_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        assert "Running with the following configuration:" in result.output

        assert "tagged-files: []" in result.output


def test_config():

    file_content = """
    [cactuskeeper]
    tagged-files =
        version_info.json
        some_other_file.py
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("setup.cfg", "w") as f:
            f.write(file_content)

        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        assert "Running with the following configuration:"

        assert (
            "tagged-files: ['version_info.json', 'some_other_file.py']" in result.output
        )


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

    @pytest.mark.parametrize("ignore_issues", [[], ["#123"]])
    def test_check_release_clean(self, ignore_issues, tmpdir):
        """
            release branches are clean if no earlier releases hold fixes
            not in this release
        """
        repo = MockRepo(branches=["master", "release/v0.9", "release/v0.8"])

        repo.add_commit("release/v0.9", "release: v0.8", sha=0)
        repo.add_commit("release/v0.9", "release: v0.9", sha=1)
        repo.add_commit("release/v0.9", "fix: bla \n blubi #123")
        repo.add_commit("release/v0.9", "fix: foo \n foo #456")

        repo.add_existing_commit("release/v0.8", 0)

        repo.add_existing_commit("master", 0)
        repo.add_existing_commit("master", 1)
        repo.add_commit("master", "fix: foo \n foo #456")

        write_config_file(str(tmpdir), {"ignore_issues": ",".join(ignore_issues)})

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            runner = CliRunner()

            result = runner.invoke(cli, ["--repo", str(tmpdir), "check"])

            # master is only clean, when #123 is ignored
            if ignore_issues:
                assert result.exit_code == 0
            else:
                assert result.exit_code == 1
                assert "release/v0.9" in result.output
                assert "#123\tfix: bla" in result.output

            repo._active_branch = "release/v0.8"

            result = runner.invoke(cli, ["check"])
            # release/v0.8 is clean
            assert result.exit_code == 0

    def test_check_clean_with_issues(self):
        """
            Check that a branch is clean if issue fixes on the other branch exist, but also
            on this branch
        """
        repo = MockRepo(branches=["master", "release/v0.9"])

        repo.add_commit("release/v0.9", "release: v0.9", sha=1)
        repo.add_commit("release/v0.9", "fix: bla \n blubi #123")

        repo.add_existing_commit("master", 1)
        repo.add_commit("master", "fix: bla \n blubi #123")

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            runner = CliRunner()

            result = runner.invoke(cli, ["check"])
            # master is clean
            assert result.exit_code == 0
            assert "The current branch is clean" in result.output


class TestRelease:
    @pytest.fixture()
    def setup_mock_repo(self):
        repo = MockRepo(branches=["master"])

        repo.add_commit("master", "base", sha="12345")

        repo.add_commits(
            "master",
            [
                "fix: something0 \n #0",
                "release: v1.2.3 \n info",
                "fix: something1 \n #1",
                "fix: something2 \n #2",
            ],
        )

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            yield

    def test_latest_commit_already_a_release(self):
        repo = MockRepo(branches=["master"])

        repo.add_commit("master", "release: v1.2.3 \n info")

        with mock.patch("cactuskeeper.cli.Repo", return_value=repo):
            runner = CliRunner()
            result = runner.invoke(cli, ["release"])

            assert result.exit_code == 0
            assert "Last commit is already a release." in result.output

    def test_release_no_custom_base(self, setup_mock_repo):
        runner = CliRunner()
        result = runner.invoke(cli, ["release"], input="n\n")

        assert result.exit_code == 0
        assert "The last release on the branch is 1.2.3." in result.output

        assert "fix: something2" in result.output
        assert "fix: something1" in result.output

        assert "fix: something0" not in result.output

    def test_release_custom_base(self, setup_mock_repo):
        runner = CliRunner()
        result = runner.invoke(cli, ["release"], input="y\n12345\nn\n")

        assert result.exit_code == 0
        assert "The last release on the branch is 1.2.3." in result.output

        assert "fix: something2" in result.output
        assert "fix: something1" in result.output
        assert "fix: something0" in result.output
        assert "The specified commit was not found." not in result.output

    def test_release_custom_base_not_found(self, setup_mock_repo):
        runner = CliRunner()
        result = runner.invoke(cli, ["release"], input="y\nidonotexist\n12345\nn\n")

        assert result.exit_code == 0
        assert "The last release on the branch is 1.2.3." in result.output

        assert "fix: something2" in result.output
        assert "fix: something1" in result.output
        assert "fix: something0" in result.output
        assert "The specified commit was not found." in result.output
