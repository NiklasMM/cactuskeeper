from collections import defaultdict

import mock


class MockRepo(mock.MagicMock):

    sha_counter = 0

    def __init__(self, branches):
        super().__init__()
        self.branches = branches
        self.commits = defaultdict(list)
        self.commits_by_sha = {}
        self._active_branch = None

    def add_commit(self, branch, commit_message, sha=None):
        if sha is None:
            sha = self.sha_counter
            self.sha_counter += 1

        commit = mock.Mock(message=commit_message, hexsha=str(sha), parents=[])
        # try to mock the parents list
        try:
            self.commits[branch][-1].parents.append(commit)
        except IndexError:
            pass
        self.commits[branch].append(commit)
        self.commits_by_sha[sha] = commit

    def add_commits(self, branch, commit_messages):
        for message in commit_messages:
            self.add_commit(branch, message)

    def add_existing_commit(self, branch, sha):
        self.commits[branch].append(self.commits_by_sha[sha])

    def iter_commits(self, branch, max_count=None):

        for commit in self.commits[branch]:
            yield commit

    @property
    def active_branch(self):
        if self._active_branch is None:
            return self.branches[0]
        else:
            return self._active_branch
