
from distutils.version import StrictVersion
import re

import pytest

from cactuskeeper.git import (
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
            [StrictVersion("1.23"), StrictVersion("0.4")]
        ),
        (
            ("release/v0.4", "release/v1.23", "some_other_branch"),
            [StrictVersion("1.23"), StrictVersion("0.4")]
        )
    ]
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


@pytest.mark.parametrize("empty", [True, False])
def test_get_latest_release_commit(empty):

    repo = MockRepo(branches=["master"])
    if not empty:
        repo.add_commits(
            "master", [
                "fix: something0 \n #0",
                "release: 1.2",
                "fix: something1 \n #1",
                "release: v1.2.1",
                "fix: something2 \n #2",
                "dev: something unrelated"
            ]
        )
    release = get_latest_release_commit(repo, "master")

    if not empty:
        assert release.shortlog == "release: v1.2.1"
    else:
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
        "release/1.2", [
            "fix: something0 \n #0"
            "release: 1.2",
            "fix: something1 \n #1",
            "release: v1.2.1",
            "fix: something2 \n #2",
        ]
    )
    result = get_bugfixes_for_branch(repo, "release/1.2")

    assert set(result.keys()) == set(["#2", "#1", "#0", "_list"])
