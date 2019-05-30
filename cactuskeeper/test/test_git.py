from distutils.version import StrictVersion
import re

from mock import Mock
import pytest

from cactuskeeper.git import (
    CommitMetadata,
    get_bugfixes_for_branch,
    get_commits_since_commit,
    get_latest_release_commit,
    get_release_branches,
)
from cactuskeeper.test.helpers import MockRepo


@pytest.mark.parametrize(
    "branches,expected",
    [
        ([], []),
        (
            ("release/v1.23", "release/v0.4", "some_other_branch"),
            [StrictVersion("1.23"), StrictVersion("0.4")],
        ),
        (
            ("release/v0.4", "release/v1.23", "some_other_branch"),
            [StrictVersion("1.23"), StrictVersion("0.4")],
        ),
    ],
)
def test_get_release_branches(branches, expected):
    repo = MockRepo(branches=branches)

    result = get_release_branches(repo)

    assert len(expected) == len(result)

    assert [x["version"] for x in result] == expected


def test_get_release_branches_with_custom_regex():
    custom_regex = re.compile(r"version(?P<version>\d+\.\d+)")

    repo = MockRepo(branches=["release/v1.2", "version1.2", "version"])

    result = get_release_branches(repo, custom_regex)

    assert 1 == len(result)

    assert StrictVersion("1.2") == result[0]["version"]


@pytest.mark.parametrize("additional_commits", [True, False])
def test_get_latest_release_commit(additional_commits):

    repo = MockRepo(branches=["master"])
    repo.add_commits("master", ["release: v1.2"])
    if additional_commits:
        repo.add_commits("master", ["fix: something1 \n #1"])
    release = get_latest_release_commit(repo, "master")
    assert release.shortlog == "release: v1.2"


def test_get_latest_release_commit_empty_repo():
    repo = MockRepo(branches=["master"])
    release = get_latest_release_commit(repo, "master")
    assert release is None


def test_get_commits_since_commit():

    repo = MockRepo(branches=["master"])

    # add some commits from before the base commit
    repo.add_commits("master", ["first commit", "second commit"])
    # add the base commit
    repo.add_commit("master", "base_commit", sha="123456")
    # add commits after the base commit
    repo.add_commits("master", ["release: v1.2.1", "fix: something2 \n #2"])

    commits = get_commits_since_commit(repo, "master", "123456")

    assert 2 == len(commits)
    assert "release: v1.2.1" == commits[-1].shortlog


def test_get_bugfixes_relative():
    repo = MockRepo(branches=["release/1.2", "master"])

    repo.add_commit("release/1.2", "fix: something \n more info #0", sha=1)
    repo.add_commit("release/1.2", "release: 1.2", sha=2)
    repo.add_commit("release/1.2", "fix: something \n more info #1")
    repo.add_commit("release/1.2", "release: v1.2.1")
    repo.add_commit("release/1.2", "fix: important thing \n more info #2")

    repo.add_existing_commit("master", 1)
    repo.add_existing_commit("master", 2)

    result = get_bugfixes_for_branch(repo, "release/1.2", "master")

    assert result["#2"].shortlog == "fix: important thing"
    assert result["#1"].shortlog == "fix: something"


def test_get_bugfixes_absolute():
    repo = MockRepo(branches=["release/1.2", "master"])

    repo.add_commits(
        "release/1.2",
        [
            "fix: something0 \n #0" "release: 1.2",
            "fix: something1 \n #1",
            "release: v1.2.1",
            "fix: something2 \n #2",
        ],
    )
    result = get_bugfixes_for_branch(repo, "release/1.2")

    assert set(result.keys()) == set(["#2", "#1", "#0"])


def test_commit_get_next_version():
    repo = MockRepo(branches=["master"])
    repo.add_commits("master", ["release: v1.2.0"])

    commit = get_latest_release_commit(repo, "master")

    assert "1.2.0" == commit.version
    assert "1.2.1" == commit.next_version()
    assert "1.2.1" == commit.next_version(step="bugfix")
    assert "1.3.0" == commit.next_version(step="minor")
    assert "2.0.0" == commit.next_version(step="major")


def test_commit_get_next_version_no_release():
    """ next_version for non-release commits returns None """

    commit = CommitMetadata(Mock(message="Something, but surely no release"))

    assert commit.next_version() is None
