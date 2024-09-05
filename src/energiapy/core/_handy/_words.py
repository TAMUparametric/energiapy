"""Reserved words
"""

reserved_property = ['horizon', 'network', 'land', 'cash']

reserved_component = [
    'player',
    'emission',
    'resource',
    'material',
    'process',
    'storage',
    'transit',
]

reserved_collection = [
    'components',
    'component',
    'analytical',
    'players',
    'spatial',
    'locations',
    'linkages',
    'temporal',
    'scales',
    'modes',
    'commodities',
    'emissions',
    'resources',
    'materials',
    'operations',
    'processes',
    'storages',
    'transits',
]


reserved_block = ['program', 'data', 'matrix', 'system', 'model']
reserved_engine = ['engines', 'registrar', 'taskmaster', 'tasks', 'rulebook', 'rules']

reserved = (
    reserved_component
    + reserved_collection
    + reserved_property
    + reserved_block
    + reserved_engine
)
