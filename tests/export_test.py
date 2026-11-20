"""Exercise notebook exporter setup without requiring the optional docs extra."""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from energia import export


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    package_dir = tmp_path / "src" / "energia"
    (package_dir / "library").mkdir(parents=True)
    monkeypatch.setattr(export, "__file__", str(package_dir / "export.py"))
    return tmp_path / "docs" / "examples", package_dir / "library" / "examples"


@pytest.mark.parametrize("directory_exists", [False, True])
def test_missing_notebooks_report_checkout_and_leave_output_untouched(
    checkout, monkeypatch, directory_exists
):
    notebook_dir, output_dir = checkout
    if directory_exists:
        notebook_dir.mkdir(parents=True)
    monkeypatch.setitem(sys.modules, "nbformat", None)
    monkeypatch.setitem(sys.modules, "nbconvert", None)

    with pytest.raises(SystemExit, match=r"No \.ipynb notebooks found") as error:
        export.main()

    assert str(notebook_dir) in str(error.value)
    assert "source checkout" in str(error.value)
    assert "python -m pip install -e '.[docs]'" in str(error.value)
    assert not output_dir.exists()


def test_checkout_notebook_is_exported(checkout, monkeypatch):
    notebook_dir, output_dir = checkout
    notebook_dir.mkdir(parents=True)
    (notebook_dir / "example.ipynb").write_text("{}", encoding="utf-8")
    (notebook_dir / "directory.ipynb").mkdir()

    read = Mock(return_value=object())
    script = "print('Energia example')\n"
    convert = Mock(return_value=(script, {}))
    exporter = SimpleNamespace(from_notebook_node=convert)
    monkeypatch.setitem(sys.modules, "nbformat", SimpleNamespace(read=read))
    monkeypatch.setitem(
        sys.modules, "nbconvert", SimpleNamespace(PythonExporter=lambda: exporter)
    )

    export.main()

    read.assert_called_once()
    convert.assert_called_once_with(read.return_value)
    assert [path.name for path in output_dir.iterdir()] == ["example.py"]
    assert (output_dir / "example.py").read_text(encoding="utf-8") == script
