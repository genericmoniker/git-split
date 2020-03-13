from os import fspath

from gitsplit.config import Config, SourceFile, SplitFile
from gitsplit.git import Git


def do_splits(config: Config):
    git = Git(cwd=str(config.source_file.parent))
    if any(fspath(split) == fspath(config.source_file) for split in config.split_files):
        run_extract(config, git)
    else:
        run_split(config, git)


def run_extract(config: Config, git: Git):
    source = config.source_file
    splits = config.split_files
    source_split = next(split for split in splits if fspath(split) == fspath(source))
    for split_file in splits:
        if split_file == source_split:
            continue
        commit_msg = f"Split {source.name} to {split_file.name}"
        create_branch(git, config, split_file)
        git.move(source, split_file)
        git.commit(commit_msg)
        source_diff_split = source.difference(split_file)
        with source_diff_split:
            edit_file(config, source_diff_split)
        git.add(source_split)
        with split_file:
            edit_file(config, split_file)
        git.commit(commit_msg)
        git.pop_branch()
    for split_file in splits:
        with split_file:
            edit_file(config, split_file)
        git.add(split_file)
    tree_hash = git.write_tree()
    parents = ["HEAD"] + [
        make_branch_name(source, split) for split in splits if split != source_split
    ]
    commit_hash = git.commit_tree(tree_hash, parents, f"Extract from {source.name}")
    git.merge_ff(commit_hash)
    print()


def run_split(config: Config, git: Git):
    for split_file in config.split_files:
        commit_msg = f"Split {config.source_file.name} to {split_file.name}"
        create_branch(git, config, split_file)
        git.move(config.source_file, split_file)
        git.commit(commit_msg)
        with split_file:
            edit_file(config, split_file)
        git.commit(commit_msg)
        git.pop_branch()
    merge_branches(git, config)


def create_branch(git: Git, config: Config, split_file: SplitFile):
    source_file = config.source_file
    branch_name = make_branch_name(source_file, split_file)
    git.checkout_new_branch(branch_name)


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


def merge_branches(git: Git, config: Config):
    branches = []
    for split_file in config.split_files:
        branches.append(make_branch_name(config.source_file, split_file))
    git.merge_branches(branches)
