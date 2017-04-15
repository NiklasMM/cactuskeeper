
import re
import pytest

from cactuskeeper.git import get_release_branches, get_bugfixes_for_branch
from cactuskeeper.test.helpers import MockRepo


@pytest.mark.parametrize(
    "branches,expected",
    [
        ([], []),
        (
            ("release/v1.23", "release/v0.4", "some_other_branch"),
            [(1, 23), (0, 4)]
        ),
        (
            ("release/v0.4", "release/v1.23", "some_other_branch"),
            [(1, 23), (0, 4)]
        )
    ]
)
def test_get_release_branches(branches, expected):
    repo = MockRepo(branches=branches)

    result = get_release_branches(repo)

    assert expected == [(x[1][0], x[1][1]) for x in result]


def test_get_release_branches_with_custom_regex():
    custom_regex = re.compile(r"version(?P<major>\d+)\.(?P<minor>\d+)")

    repo = MockRepo(branches=["release/v1.2", "version1.2", "version"])

    result = get_release_branches(repo, custom_regex)

    assert [(1, 2)] == [(x[1][0], x[1][1]) for x in result]


def test_get_bugfixes():
    repo = MockRepo(branches=["release/1.2", "master"])

    repo.add_commit("release/1.2", "fix: something #2")
    repo.add_commit("release/1.2", "release: v1.2.1")
    repo.add_commit("release/1.2", "fix: something #1")
    repo.add_commit("release/1.2", "release: 1.2", sha=2)
    repo.add_commit("release/1.2", "fix: something #0", sha=1)

    repo.add_existing_commit("master", 1)
    repo.add_existing_commit("master", 2)

    result = get_bugfixes_for_branch(repo, "release/1.2", "master")

    assert result == ["#2", "#1"]
