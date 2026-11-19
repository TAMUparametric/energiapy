"""Model construction with a shared list of initializers."""

import pytest

from energia import Model


@pytest.mark.parametrize("second_uses_defaults", [True, False])
def test_reusing_initializers_across_models(second_uses_defaults):
    calls = []

    def record(model):
        calls.append(model.name)

    initializers = [record]
    defaults = Model().init
    first = Model("first", init=initializers)
    second = Model("second", init=initializers, default=second_uses_defaults)

    assert initializers == [record]
    initializers.clear()
    assert first.init == [record, *defaults]
    assert second.init == ([record, *defaults] if second_uses_defaults else [record])
    assert ("capacity" in second.cookbook) is second_uses_defaults
    assert calls == ["first", "second"]
