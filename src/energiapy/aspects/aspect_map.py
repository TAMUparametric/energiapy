from .capacity import Capacity
from .resflow import Consume, Discharge
from .resflowcap import Produce, Store, Transport

# *ResFlow

resflow_res_attrs = {
    'discharge': Discharge,
    'consume': Consume,
}

resflow_attrs = {**resflow_res_attrs}


# *ResFlowCap

resflowcap_pro_attrs = {
    'produce': Produce,
}

resflowcap_str_attrs = {
    'store': Store,
}

resflowcap_trn_attrs = {
    'transport': Transport
}

resflowcap_attrs = {**resflowcap_pro_attrs, **
                    resflowcap_str_attrs, **resflowcap_trn_attrs}

# *CashFlow

cashflow_res_attrs = {
    'sell_cost': SellCost,
    'buy_cost': BuyCost,
    'credit': Credit,
    'penalty': Penalty
}

cashflow_opn_attrs = {
    'capex': Capex,
    'capex_pwl': CapexPwl,
    'fopex': Fopex,
    'vopex': Vopex,
    'incidental': Incidental
}

cashflow_str_attrs = {'store_cost': StoreCost}

cashflow_trn_attrs = {'transport_cost': TransportCost}

cashflow_spt_attrs = {
    'land_cost': LandCost
}

cashflow_attrs = {**cashflow_res_attrs, **cashflow_opn_attrs, **
                  cashflow_str_attrs, **cashflow_trn_attrs, **cashflow_spt_attrs}

# CashFlowCap



# *ResLoss

resloss_str_attrs = {
    'str_loss': StrLoss
}

resloss_trn_attrs = {
    'trn_loss': TrnLoss
}

resloss_attrs = {
    **resloss_str_attrs, **resloss_trn_attrs
}


# * Capacity

capacity_opn_attrs = {
    'capacity': Capacity,
}

capacity_attrs = {**capacity_opn_attrs}

# * LandUse


landuse_opn_attrs = {
    'land_use': LandUse
}

landuse_attrs = {**landuse_opn_attrs}

# * LandCap

landcap_spt_attrs = {
    'land_cap': LandCap,
}

landcap_attrs = {**landcap_spt_attrs}

# * Life

life_opn_attrs = {
    'introduce': Introduce,
    'retire': Retire,
    'lifetime': Lifetime,
    'pfail': Pfail,
    'trl': Trl
}

life_attrs = {**life_opn_attrs}

# * Emission
emission_init = [
    ('gwp', 'kg CO2 eq.', 'Global Warming Potential'),
    ('ap', 'mol eq', 'Acidification Potential'),
    ('epm', 'kg P eq', 'Eutrophication Potential (Marine)'),
    ('epf', 'kg P eq', 'Eutrophication Potential (Freshwater)'),
    ('ept', 'kg P eq', 'Eutrophication Potential (Terrestrial)'),
    ('pocp', 'kg NMVOC eq', 'Photochemical Ozone Creation Potential'),
    ('odp', 'kg CFC 11 eq', 'Ozone Depletion Potential'),
    ('adpmn', 'kg Sb eq', 'Abiotic Depletion Potential (Mineral)'),
    ('adpmt', 'kg Sb eq', 'Abiotic Depletion Potential (Metal)'),
    ('adpf', 'MJ', 'Abiotic Depletion Potential (Fossil)'),
    ('wdp', 'm^3', 'Water Deprivation Potential')
]

emission_comp_attrs = {i[0]: Emission for i in emission_init}

emissioncap_spt_attrs = {f'{i[0]}_cap': EmissionCap for i in emission_init}

emission_attrs = {**emission_comp_attrs, **emissioncap_spt_attrs}

# *Component

res_attrs = {**resflow_attrs, **resflowcap_attrs,
             **resloss_attrs, **emission_attrs}

common_opn_attrs = {**cashflow_opn_attr, **
                    capacity_opn_attrs, **land_opn_attrs, **life_opn_attrs}

pro_attrs = {}


aspect_map = {**res_attrs, **opn_attrs, **spt_attrs, **emission_attrs}
