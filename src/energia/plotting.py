"""Read existing physical quantities and delegate every chart to Gana."""

from __future__ import annotations

from dataclasses import fields
from itertools import product

from gana import V
from gana.plotting import ElementPlots, PlotMethods, Series, snapshot

from .components.measure.unit import Unit


def _period_root(periods):
    """Retain the declared time scale behind an integer or slice selection."""
    while periods is not None and periods.parent is not None:
        periods = periods.parent
    return periods


def _matches(requested, registered):
    """Match explicit indices without substituting a hierarchy total."""
    for field in fields(requested):
        value = getattr(requested, field.name)
        if field.name == "samples":
            if value and requested.index_binds != registered.index_binds:
                return False
        elif value is not None:
            actual = getattr(registered, field.name)
            if field.name == "periods":
                value = _period_root(value)
            if value is not actual:
                return False
    return True


def _resolve(source):
    """Require one registered domain before reading a physical quantity."""
    state = getattr(source, "__dict__", {})
    aspect = state.get("aspect", source)
    if "domains" not in getattr(aspect, "__dict__", {}):
        message = "Supply an Energia Sample or Aspect"
        raise TypeError(message)
    requested = state.get("domain")
    if requested is not None and requested.lag is not None:
        message = "Select stored periods explicitly instead of a lagged expression"
        raise ValueError(message)
    candidates = [
        domain
        for domain in aspect.domains
        if requested is None or _matches(requested, domain)
    ]
    if not candidates:
        message = "No registered result domain matches this selection"
        raise ValueError(message)
    if len(candidates) != 1:
        message = (
            "Ambiguous result domain; select the location, periods, "
            "and related activity explicitly"
        )
        raise ValueError(message)
    if state.get("report", False):
        message = "Select the physical quantity rather than its reporting binary"
        raise ValueError(message)
    return aspect, candidates[0], requested


def _unit(primary):
    """Read the declared basis; never infer a rate or integrate over time."""
    seen = set()
    while primary is not None and id(primary) not in seen:
        if isinstance(primary, Unit):
            return primary.label or primary.name or None
        seen.add(id(primary))
        primary = getattr(primary, "basis", None)
    return None


def _name(component):
    return component.label or component.name


def _time_axis(domain):
    """Map complete time coordinates to ordered model-period positions."""
    indices = domain.__dict__["I"]
    times = domain.periods.__dict__["I"]
    times = times if isinstance(times, tuple) else (times,)
    positions = tuple(
        next(n for n, index in enumerate(indices) if index is time) for time in times
    )
    coordinates = tuple(tuple(map(id, key)) for key in product(*times))
    return positions, coordinates


def _period_positions(periods, size):
    """Apply nested slices to model-period positions, retaining their offsets."""
    if periods is None or periods.parent is None:
        return tuple(range(size))
    positions = _period_positions(periods.parent, size)
    if periods.slice is not None:
        return positions[periods.slice]
    return (positions[periods.n],)


def _members(index):
    """A variable used as an index denotes the quantity, not its scalar rows."""
    return {id(index)} if isinstance(index, V) else {id(atom) for atom in index}


def _belongs(ids, members):
    return len(ids) == len(members) and all(
        atom in allowed for atom, allowed in zip(ids, members)
    )


def _rows(aspect, domain, time_positions, coordinates, selected, *, n_sol):
    """Select existing rows without creating a Gana variable projection."""
    variable = vars(aspect.program).get(aspect.name)
    if variable is None:
        message = "The selected aspect has no registered variable"
        raise ValueError(message)
    saved = snapshot(variable, n_sol=n_sol)
    members = tuple(_members(index) for index in domain.__dict__["I"])
    lookup = {key: n for n, key in enumerate(coordinates)}
    groups = {}
    for key, value in zip(saved.coordinates, saved.values):
        ids = tuple(map(id, key))
        if not _belongs(ids, members):
            continue
        time = tuple(ids[n] for n in time_positions)
        position = lookup[time]
        if position in selected:
            category = tuple(
                atom for n, atom in enumerate(ids) if n not in time_positions
            )
            groups.setdefault(category, []).append((position, time, value, key))
    return groups


def records(source, *, n_sol=0):
    """Return Gana series for one registered Energia result domain.

    The complete temporal tuple becomes an ordered horizontal axis. Remaining
    coordinates identify series. Values retain their stored basis: occurrence
    weights, durations, hierarchy totals and incidental costs are not reapplied.
    Explicitly select time and space when more than one registered domain matches.
    """
    aspect, domain, requested = _resolve(source)
    time_positions, coordinates = _time_axis(domain)
    periods = None if requested is None else requested.periods
    selected = _period_positions(periods, len(coordinates))
    groups = _rows(aspect, domain, time_positions, coordinates, selected, n_sol=n_sol)
    if not groups:
        message = "The selection contains no registered result coordinates"
        raise ValueError(message)
    return tuple(
        _series(source, aspect, domain, category, rows, selected=selected, n_sol=n_sol)
        for category, rows in groups.items()
    )


def _category(domain):
    """Keep technology encodings consistent across quantities and panels."""
    return tuple(dict.fromkeys(id(s.domain.primary) for s in domain.samples)) or (
        id(domain.primary),
    )


def _label(aspect, domain, key, n_sol):
    label = f"{_name(domain.primary)} {aspect.name}"
    if domain.samples:
        label += " / " + ", ".join(
            dict.fromkeys(_name(s.domain.primary) for s in domain.samples),
        )
    if domain.space is not aspect.model.network:
        label += f" ({_name(domain.space)})"
    if n_sol:
        label += f" [solution {n_sol}]"
    if domain.modes is not None:
        label += f" ({key[-1].name})"
    return label


def _series(source, aspect, domain, category, rows, *, selected, n_sol):
    order = {position: n for n, position in enumerate(selected)}
    rows = sorted(rows, key=lambda row: order[row[0]])
    label = _label(aspect, domain, rows[0][3], n_sol)
    return Series(
        x=tuple(row[0] for row in rows),
        values=tuple(row[2] for row in rows),
        coordinates=tuple(row[1] for row in rows),
        domain=(id(aspect.model), id(domain.periods)),
        key=(
            id(aspect.model),
            _category(domain),
            id(domain.space),
            category[-1] if domain.modes is not None else None,
            n_sol,
        ),
        label=label,
        xlabel=f"{_name(domain.periods)} (model period)",
        n_sol=n_sol,
        source=source,
        unit=_unit(domain.primary),
    )


def _bounds(options, n_sol):
    for name in ("x", "lower", "upper"):
        value = options.get(name)
        if value is not None and "aspect" in getattr(value, "__dict__", {}):
            bounds = records(value, n_sol=n_sol)
            if len(bounds) != 1:
                message = "An auxiliary quantity must select one series"
                raise ValueError(message)
            options[name] = bounds[0]


def _arguments(sources, options):
    options = dict(options)
    n_sol = options.pop("n_sol", 0)
    data = tuple(
        record for source in sources for record in records(source, n_sol=n_sol)
    )
    _bounds(options, n_sol)
    units = {record.unit for record in data}
    if len(units) > 1:
        message = "Quantities with different or unknown units need separate panels"
        raise ValueError(message)
    if data:
        options.setdefault("ylabel", data[0].unit or "Value (unit unspecified)")
    return data, options


class QuantityPlots(ElementPlots):
    """Samples and aspects use Gana's chart methods and return Gana plots."""

    def _plot_arguments(self, sources, options):
        _, options = super()._plot_arguments(sources, options)
        return _arguments((self,), options)


class ModelPlots(PlotMethods):
    """A model collects selected quantities through the same adapter."""

    def _plot_arguments(self, sources, options):
        if any(source.model is not self for source in sources):
            message = "Every plotted quantity must belong to this model"
            raise ValueError(message)
        return _arguments(sources, options)
