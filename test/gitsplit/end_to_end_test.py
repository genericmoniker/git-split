import shutil
import sys
from pathlib import Path
from subprocess import run
from unittest import mock

import pytest

from gitsplit.main import main


@pytest.fixture(name="repo")
def repo_fixture(tmp_path):
    run(["git", "init"], check=True, cwd=str(tmp_path))
    file = tmp_path / "foods"
    edit(file, "apple\ncelery\ncheese\n", "Alice <alice>")
    edit(file, "eggs\ngrape\nlettuce\n", "Bob <bob>")
    edit(file, "milk\norange\npeas\n", "Carol <carol>")
    return tmp_path


def edit(path: Path, text: str, author: str):
    """Edit a file and commit the edited file with git.

    :param path: path to the file to edit, which must be in a git repo.
    :param text: text to append to the file.
    :param author: author to use for the commit.
    """
    cwd = str(path.parent)
    exists = path.exists()
    with path.open("a") as f:
        f.write(text)
    if not exists:
        run(["git", "add", str(path)], check=True, cwd=cwd)
    run(["git", "commit", "-am", "msg", f'--author="{author}"'], check=True, cwd=cwd)


def test_split(repo):
    """Test Raymond Chen's split example."""
    config_src = Path(__file__).parent / "foods.split.toml"
    config_file = repo / config_src.name
    shutil.copy(config_src, config_file)

    with mock.patch.object(sys, "argv", ["git-split", str(config_file)]):
        main()

    dairy = repo / "dairy"
    fruits = repo / "fruits"
    veggies = repo / "veggies"
    assert dairy.read_text() == "cheese\neggs\nmilk\n"
    assert fruits.read_text() == "apple\ngrape\norange\n"
    assert veggies.read_text() == "celery\nlettuce\npeas\n"

    # TODO: Further assertions... pylint: disable=fixme
