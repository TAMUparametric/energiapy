"""The nature of attributes that feature in Components of the System model"""

nature = {
    'player': {
        'bounds': ['has', 'needs'],
    },
    'emission': {
        'bounds': ['emit'],
    },
    'cash': {
        'bounds': ['spend', 'earn'],
    },
    'cmd_used': {
        'expenses': ['cost'],
        'bounds': ['use'],
        'emitted': ['emission'],
    },
    'resource': {
        'expenses': ['buy_price', 'sell_price', 'credit', 'penalty'],
        'bounds_trade': ['buy', 'sell'],
        'bounds_transit': ['ship', 'receive'],
        'bounds': ['buy', 'sell', 'ship', 'receive'],
        'emitted': ['buy_emission', 'sell_emission', 'loss_emission'],
    },
    'operational': {
        'expenses': ['capex', 'opex'],
        'bounds': ['capacity', 'operate'],
        'landuse': ['land'],
        'materialuse': ['material'],
        'resourcebnds': ['buy', 'sell'],
        'emitted': ['emission'],
    },
    'resourceloss': ['loss'],
}
