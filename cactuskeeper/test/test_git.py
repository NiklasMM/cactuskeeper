import mock
import re
from collections import defaultdict
import pytest

from cactuskeeper.git import get_release_branches, get_bugfixes_for_branch


class MockRepo(mock.MagicMock):

    sha_counter = 0

    def __init__(self, branches):
        super().__init__()
        self.branches = branches
        self.commits = defaultdict(list)
        self.commits_by_sha = {}

    def add_commit(self, branch, commit_message, sha=None):
        if sha is None:
            sha = self.sha_counter
            self.sha_counter += 1

        commit = mock.Mock(message=commit_message, binsha=sha)
        self.commits[branch].append(commit)
        self.commits_by_sha[sha] = commit

    def add_existing_commit(self, branch, sha):
        self.commits[branch].append(self.commits_by_sha[sha])

    def iter_commits(self, branch, max_count=None):

        for commit in self.commits[branch]:
            yield commit


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
