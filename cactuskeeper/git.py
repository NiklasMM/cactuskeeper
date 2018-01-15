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
        if m is not None:  # pragma: no cover, the regex matches everything
            if m.group("issue"):
                self.issue = m.group("issue")
            if m.group("version"):
                self.version = m.group("version")

    def next_version(self, step="bugfix"):
        """
            Calculates the next version for release commits.

            :param step:
                The level on which the next version should be created.
                Can be "major", "minor" or "bugfix"

            :return:
                The next version as a string or None if the commit is not a release commit.
        """
        if not self.version:
            return None

        current_version = StrictVersion(self.version)

        major = current_version.version[0]
        minor = current_version.version[1]
        bugfix = current_version.version[2]

        if step == "major":
            major = major + 1
            minor = 0
            bugfix = 0
        if step == "minor":
            minor = minor + 1
            bugfix = 0
        if step == "bugfix":
            bugfix = bugfix + 1

        return ".".join(map(lambda x: str(x), [major, minor, bugfix]))


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
    """
        Finds the lates release commit in a repo on a given branch.

        :param repo:
            The repository to process.
        :param branch:
            The branch on which the function should look for commits.

        :return:
            A CommitMetadata object for the latest release commit or
            None if no release commit could be found.
    """

    for commit in repo.iter_commits(branch):
        if commit.message.startswith("release:"):
            return CommitMetadata(commit)

    # no release found
    return None


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

    if base_branch is not None:
        base_commits = set(c.hexsha for c in repo.iter_commits(base_branch))
        test = lambda x: x.hexsha not in base_commits
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
