"""The nature of attributes that feature in Components of the System model"""

nature = {
    'players': {
        'quantify': ['has', 'needs'],
    },
    'emissions': {
        'quantify': ['emit'],
    },
    'cash': {
        'quantify': ['spend', 'earn'],
    },
    'land': {
        'expenses': ['cost'],
        'quantify': ['use'],
        'emitted': ['emission'],
    },
    'materials': {
        'expenses': ['cost'],
        'quantify': ['use'],
        'emitted': ['emission'],
    },
    'resources': {
        'expenses': ['buy_price', 'sell_price', 'credit', 'penalty'],
        'quantify': ['buy', 'sell', 'ship', 'deliver'],
        'emitted': ['emission'],
    },
    'processes': {
        'expenses': ['capex', 'opex'],
        'quantify': ['capacity', 'operate'],
        'landuse': ['land'],
        'resourcebnds': ['buy', 'sell'],
        'resourceexps': ['buy_price', 'sell_price', 'credit', 'penalty'],
        'materialuse': ['material'],
        'emitted': ['emission'],
    },
    'storages': {
        'expenses': ['capex', 'opex'],
        'quantify': ['capacity', 'operate'],
        'landuse': ['land'],
        'materialuse': ['material'],
        'emitted': ['emission'],
        'loss': ['loss'],
    },
    'transits': {
        'expenses': ['capex', 'opex'],
        'quantify': ['capacity', 'operate'],
        'landuse': ['land'],
        'resourcebnds': ['ship', 'deliver'],
        'materialuse': ['material'],
        'emitted': ['emission'],
        'loss': ['loss'],
    },
}
