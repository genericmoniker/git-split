from os import fspath
from subprocess import run


class Git:
    def __init__(self, cwd):
        self.cwd = cwd

    def _git(self, *args):
        cmd = ["git"]
        cmd.extend(args)
        return run(cmd, check=True, cwd=self.cwd)

    def checkout_new_branch(self, branch_name: str):
        return self._git("checkout", "-b", branch_name)

    def move(self, source, destination):
        return self._git("mv", fspath(source), fspath(destination))

    def commit(self, message):
        """Stage and commit tracked, modified files."""
        return self._git("commit", "-am", message)

    def pop_branch(self):
        """Go back to the previously checked out branch."""
        return self._git("checkout", "-")

    def merge_branches(self, branches):
        return self._git("merge", *branches)
