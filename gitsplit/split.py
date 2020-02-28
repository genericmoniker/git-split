from os import fspath
from subprocess import run

from gitsplit.config import Config, SourceFile, SplitFile


def do_splits(config: Config):
    cwd = str(config.source_file.parent)
    for split_file in config.split_files:
        commit_msg = f"Split {config.source_file.name} to {split_file.name}"
        create_move_branch(config, split_file)
        commit(cwd, commit_msg)
        with split_file:
            edit_file(config, split_file)
        commit(cwd, commit_msg)
        pop_branch(cwd)
    merge_branches(config, cwd)


def create_move_branch(config: Config, split_file: SplitFile):
    source_file = config.source_file
    cwd = str(source_file.parent)
    branch_name = make_branch_name(source_file, split_file)
    run(["git", "checkout", "-b", branch_name], check=True, cwd=cwd)
    run(["git", "mv", fspath(source_file), fspath(split_file)], check=True, cwd=cwd)


def make_branch_name(source_file: SourceFile, split_file: SplitFile) -> str:
    return f"split-{escape(source_file.name)}-to-{escape(split_file.name)}"


def escape(filename: str) -> str:
    for char in [".", "~", "^", ":", " ", "/", "\\", "?", "[", "*"]:
        if char in filename:
            filename = filename.replace(char, "-")
    return filename


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


def merge_branches(config: Config, cwd):
    run(["git", "branch", "-a"], check=True, cwd=cwd)
    cmd = ["git", "merge"]
    for split_file in config.split_files:
        cmd.append(make_branch_name(config.source_file, split_file))
    run(cmd, check=True, cwd=cwd)
