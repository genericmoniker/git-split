# git-split

**Warning: This project is under active development and probably isn't ready to
use yet!** Please check back as it matures.

A history-preserving file splitter for Git.

You create a config file indicating how you'd like to split a file, and
git-split will perform the Git operations to split that file **and** perform
edits to the resulting files to include just the parts you specified, all while
maintaining the `git blame` history.

Sometimes a module starts out simple, but grows to the point where it would be
better if it were divided into two (or many!) modules instead. It is easy to
copy and paste the appropriate parts of a file into new files, but that usually
results in the loss of the valuable line-by-line history that Git maintains.

You can preserve the history with the right combination of branching, moving,
editing, committing and merging, but it can be tedious and fiddly. Furthermore,
it requires that you delete all of the text that you *don't* want in the newly
split-off file, which becomes onerous if you've got a large source file that
you want to split into several files. You end up deleting the same blocks of
text over and over again.

Using this utility, you create a
[TOML-formatted](https://github.com/toml-lang/toml) config file specifying the
source file to start with, the resulting files to split to, and which lines
from the source file you want to include in each split out file. After running
the utility, you'll end up with the files as specified, merged into the
currently checked out Git branch.

## A Simple Example


## Installation


## Usage Tips

Start with an unmodified working tree. git-split will abort otherwise. "Please,
commit your changes or stash them before running git-split." 

The split will be a merge into your current branch. You may want to create and
checkout a branch for that specifically.

## Development setup

```sh
# If poetry isn't installed
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry

# Install dependencies
poetry install

# Setup pre-commit and pre-push hooks
poetry run pre-commit install -t pre-commit
poetry run pre-commit install -t pre-push

# To run pre-commit hooks manually (without a commit)
poetry run pre-commit run --all-files
```
