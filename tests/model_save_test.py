"""Round-trip solver results and preserve destinations when saves fail."""

import numpy as np
import pytest
from dill import load

from energia import Model, Resource
from energia.represent import model as model_module


@pytest.fixture
def model(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    model = Model("save_test")
    model.labor = Resource(take=True, price=3)
    model.labor.release == 2
    return model


def test_save_uses_latest_program_result_and_accepts_an_index(model, tmp_path):
    assert model.solution is None  # Exercise the cached model attribute.
    model.cash.spend.opt()
    model.program.opt()

    default_path = tmp_path / "save_test.energia"
    default_path.write_bytes(b"previous save")
    model.save("dill")
    explicit_path = tmp_path / "first-result"
    model.save(path=str(explicit_path), n_sol=0)

    for path, index in [(default_path, 1), (explicit_path, 0)]:
        expected = model.program.solutions[index]
        with path.open("rb") as file:
            result = load(file)
        assert type(result) is type(expected)
        assert result.name == expected.name
        assert result._ == expected._
        assert result.asdict()["spend"] == [6.0, 6.0]


def test_save_preserves_the_parametric_result(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    model = Model()
    model.labor = Resource(take=True, price=(7.86, 8.89))
    model.labor.release == 2
    model.cash.spend.obj()
    model.solve()

    path = tmp_path / "parametric.energia"
    model.save(path=path)
    with path.open("rb") as file:
        result = load(file)
    assert type(result) is type(model.program.solution)
    assert result.evaluate_objective(np.array([[8.375]])) == pytest.approx(16.75)


@pytest.mark.parametrize("n_sol", [None, 0])
def test_unsolved_save_fails_before_opening_any_file(model, tmp_path, monkeypatch, n_sol):
    path = tmp_path / "save_test.energia"
    path.write_bytes(b"previous save")

    def unexpected_open(*args, **kwargs):
        pytest.fail("An unsolved save tried to open a temporary file")

    monkeypatch.setattr(model_module, "NamedTemporaryFile", unexpected_open)
    with pytest.raises(RuntimeError, match="Solve the model"):
        model.save(n_sol=n_sol)
    assert path.read_bytes() == b"previous save"


def test_invalid_index_preserves_existing_file(model, tmp_path):
    model.cash.spend.opt()
    path = tmp_path / "save_test.energia"
    path.write_bytes(b"previous save")

    with pytest.raises(KeyError):
        model.save(n_sol=1)
    assert path.read_bytes() == b"previous save"


def test_unsupported_format_preserves_existing_file(model, tmp_path):
    path = tmp_path / "save_test.energia"
    path.write_bytes(b"previous save")

    with pytest.raises(ValueError, match="Unknown type json"):
        model.save("json")
    assert path.read_bytes() == b"previous save"


def test_failed_serialization_preserves_existing_file_and_removes_temp_file(
    model, tmp_path, monkeypatch
):
    model.cash.spend.opt()
    path = tmp_path / "save_test.energia"
    path.write_bytes(b"previous save")
    original_files = set(tmp_path.iterdir())

    def fail_after_writing(solution, file):
        file.write(b"incomplete save")
        file.flush()
        assert path.read_bytes() == b"previous save"
        raise OSError("write failed")

    monkeypatch.setattr(model_module, "dump", fail_after_writing)
    with pytest.raises(OSError, match="write failed"):
        model.save(path=path)
    assert path.read_bytes() == b"previous save"
    assert set(tmp_path.iterdir()) == original_files
