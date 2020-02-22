# git-split

## Usage

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
