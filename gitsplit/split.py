from os import fspath
from subprocess import run

from gitsplit.config import Config, SplitFile


def do_splits(config: Config):
    cwd = str(config.source_file.parent)
    for split_file in config.split_files:
        create_move_branch(config, split_file)
        with split_file:
            edit_file(config, split_file)
        commit(cwd, f"Split {config.source_file.name} to {split_file.name}")
        pop_branch(cwd)


def create_move_branch(config: Config, split_file: SplitFile):
    source_file = config.source_file
    cwd = str(source_file.parent)

    # branch_name from the SplitFile? Optionally specify in the config?
    # At least escape the file names?
    # Yes, we need the branch name later to do the merge...
    branch_name = f"split-{source_file.name}-to-{split_file.name}"
    run(["git", "checkout", "-b", branch_name], check=True, cwd=cwd)
    run(["git", "mv", fspath(source_file), fspath(split_file)], check=True, cwd=cwd)


def edit_file(config: Config, split_file: SplitFile):
    for line_number, line in enumerate(config.source_file.lines, start=1):
        if line_number in split_file:
            split_file.write(line)


def commit(cwd, message):
    """Stage and commit tracked, modified files."""
    run(["git", "commit", "-am", message], check=True, cwd=cwd)


def pop_branch(cwd):
    """Go back to the previously checked out branch."""
    run(["git", "checkout", "-"], check=True, cwd=cwd)
