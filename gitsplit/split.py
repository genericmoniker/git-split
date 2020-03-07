from gitsplit.config import Config, SourceFile, SplitFile
from gitsplit.git import Git


def do_splits(config: Config):
    git = Git(cwd=str(config.source_file.parent))
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
