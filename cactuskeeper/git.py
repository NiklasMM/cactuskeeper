from collections import namedtuple
from distutils.version import StrictVersion
from itertools import takewhile
import re

RELEASE_BRANCHES = re.compile(r"release/v(?P<version>\d+\.\d+(\.\d+)?)")

COMMIT_REGEX = re.compile(
    r"^(?P<shortlog>(release: v(?P<version>(\d+)\.(\d+)\.(\d)))|.+)"
    r"[^#]*(?P<issue>#\d+)?"
)


class CommitMetadata:

    def __init__(self, commit):
        self.shortlog = commit.message.split("\n")[0].strip()
        self.object = commit
        self.version = ""
        self.issue = ""

        m = COMMIT_REGEX.match(commit.message)
        if m is not None:
            if m.group("issue"):
                self.issue = m.group("issue")
            if m.group("version"):
                self.version = m.group("version")


def get_release_branches(repo, release_branch_re=RELEASE_BRANCHES):
    release_branches = []

    for branch in repo.branches:
        m = release_branch_re.match(str(branch))
        if m:
            version = StrictVersion(m.group("version"))
            release_branches.append({
                "version": version,
                "branch": branch
            })

    return sorted(release_branches, key=lambda x: x["version"], reverse=True)


def get_latest_release_commit(repo, branch):

    for commit in repo.iter_commits(branch):
        if commit.message.startswith("release:"):
            return CommitMetadata(commit)


def get_commits_while(repo, branch, test):
    if test is not None:
        commit_iterator = takewhile(test, repo.iter_commits(branch))
    else:
        commit_iterator = repo.iter_commits(branch)
    result = []

    for commit in commit_iterator:
        result.append(CommitMetadata(commit))
    return result


def get_bugfixes_for_branch(repo, branch, base_branch=None):

    def commit_not_in_branch(commit):
        return commit not in repo.iter_commits(base_branch)

    if base_branch is not None:
        test = commit_not_in_branch
    else:
        test = None

    commits = get_commits_while(repo, branch, test)

    result = {
        "_list": []
    }
    for commit in commits:
        if commit.version:
            continue
        if commit.issue:
            result[commit.issue] = commit
            result["_list"].append(commit)
    return result


def get_commits_since_commit(repo, branch, commit_hexsha):
    return get_commits_while(repo, branch, lambda commit: commit.hexsha != commit_hexsha)
