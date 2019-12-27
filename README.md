# git-split

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
