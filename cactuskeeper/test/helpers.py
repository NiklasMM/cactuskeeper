from collections import defaultdict
import configparser
import os
import uuid

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
            sha = str(uuid.uuid4()).replace("-", "")

        commit = mock.Mock(message=commit_message, hexsha=str(sha), parents=[])

        # try to mock the parents list
        try:
            commit.parents.append(self.commits[branch][0])
        except IndexError:
            pass

        self.commits[branch].insert(0, commit)
        self.commits_by_sha[sha] = commit

    def add_commits(self, branch, commit_messages):
        for message in commit_messages:
            self.add_commit(branch, message)

    def add_existing_commit(self, branch, sha):
        self.commits[branch].insert(0, self.commits_by_sha[sha])

    def iter_commits(self, branch, max_count=None):

        for commit in self.commits[branch]:
            yield commit

    @property
    def active_branch(self):
        if self._active_branch is None:
            return self.branches[0]
        else:
            return self._active_branch


def write_config_file(base_dir, content):
    """
    Writes a new setup.cfg file with a "cactuskeeper" section to a given directory.

    :param base_dir:
        The directory the config file will be placed in.
    :type base_dir:
        str
    :param content:
        A dictionary holding cactuskeeper section entries as key/value pairs.
    :type content:
        dict
    """
    parser = configparser.ConfigParser()
    parser.add_section("cactuskeeper")
    for key, value in content.items():
        parser.set("cactuskeeper", key, value)

    with open(os.path.join(base_dir, "setup.cfg"), "w") as f:
        parser.write(f)
