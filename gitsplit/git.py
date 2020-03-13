from os import fspath
from subprocess import PIPE, run


class Git:
    def __init__(self, cwd, commit_no_verify: bool):
        self.cwd = cwd
        self.commit_no_verify = commit_no_verify

    def _git(self, *args):
        cmd = ["git"]
        cmd.extend(args)
        return run(cmd, check=True, cwd=self.cwd, stdout=PIPE)

    def add(self, *args):
        """Add the files in args to the staging area."""
        return self._git("add", *(fspath(f) for f in args))

    def checkout_new_branch(self, branch_name: str):
        return self._git("checkout", "-b", branch_name)

    def commit(self, message):
        """Stage and commit tracked, modified files."""
        args = ["commit", "-am", message]
        if self.commit_no_verify:
            args.append("--no-verify")
        return self._git(*args)

    def commit_tree(self, tree_hash, parents, message):
        p_args = []
        for parent in parents:
            p_args.append("-p")
            p_args.append(parent)
        result = self._git("commit-tree", *p_args, "-m", message, tree_hash)
        return result.stdout.decode().strip()

    def merge_branches(self, branches):
        return self._git("merge", *branches)

    def merge_ff(self, commit_hash):
        return self._git("merge", "--ff-only", commit_hash)

    def move(self, source, destination):
        return self._git("mv", fspath(source), fspath(destination))

    def pop_branch(self):
        """Go back to the previously checked out branch."""
        return self._git("checkout", "-")

    def write_tree(self):
        return self._git("write-tree").stdout.decode().strip()
