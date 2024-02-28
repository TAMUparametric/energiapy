from tests.test_fixtures import single_location_scenario_variability


def test_single_location_scenario_variability_sets(single_location_scenario_variability):
    """Tests the set_dicts for the scenario"""
    assert (single_location_scenario_variability.set_dict['resources'] == [
            'resource_certain_availability', 'resource_deterministic_availability', 'resource_deterministic_demand', 'resource_deterministic_price', 'resource_deterministic_revenue'])
    assert (single_location_scenario_variability.set_dict['resources_nosell'] == [
            'resource_certain_availability', 'resource_deterministic_availability', 'resource_deterministic_price'])
    assert (single_location_scenario_variability.set_dict['resources_sell'] == [
            'resource_deterministic_demand', 'resource_deterministic_revenue'])
    assert (


        single_location_scenario_variability.set_dict['resources_store'] == [])
    assert (single_location_scenario_variability.set_dict['resources_purch'] == [
        'resource_certain_availability', 'resource_deterministic_availability', 'resource_deterministic_price'])
    assert (single_location_scenario_variability.set_dict['resources_varying_demand'] == [
        'resource_deterministic_demand'])
    assert (
        single_location_scenario_variability.set_dict['resources_certain_demand'] == [])
    assert (
        single_location_scenario_variability.set_dict['resources_uncertain_demand'] == [])
    assert (single_location_scenario_variability.set_dict['resources_varying_price'] == [
        'resource_deterministic_price'])
    assert (single_location_scenario_variability.set_dict['resources_certain_price'] == [
        'resource_certain_availability'])
    assert (
        single_location_scenario_variability.set_dict['resources_uncertain_price'] == [])
    assert (single_location_scenario_variability.set_dict['resources_varying_revenue'] == [
        'resource_deterministic_revenue'])
    assert (
        single_location_scenario_variability.set_dict['resources_certain_revenue'] == [])
    assert (
        single_location_scenario_variability.set_dict['resources_uncertain_revenue'] == [])
    assert (single_location_scenario_variability.set_dict['resources_varying_availability'] == [
        'resource_deterministic_availability'])
    assert (single_location_scenario_variability.set_dict['resources_certain_availability'] == [
        'resource_certain_availability'])
    assert (
        single_location_scenario_variability.set_dict['resources_uncertain_availability'] == [])
    assert (single_location_scenario_variability.set_dict['resources_demand'] == [
        'resource_deterministic_demand', 'resource_deterministic_revenue'])
    assert (
        single_location_scenario_variability.set_dict['resources_implicit'] == [])
    assert (single_location_scenario_variability.set_dict['processes'] == [
        'process_certain_capacity', 'process_deterministic_capacity'])
    assert (single_location_scenario_variability.set_dict['processes_full'] == [
        'process_certain_capacity', 'process_deterministic_capacity'])
    assert (
        single_location_scenario_variability.set_dict['processes_failure'] == [])
    assert (single_location_scenario_variability.set_dict['processes_materials'] == [
        'process_certain_capacity', 'process_deterministic_capacity'])
    assert (
        single_location_scenario_variability.set_dict['processes_storage'] == [])
    assert (
        single_location_scenario_variability.set_dict['processes_multim'] == [])
    assert (single_location_scenario_variability.set_dict['processes_singlem'] == [
        'process_certain_capacity', 'process_deterministic_capacity'])
    assert (
        single_location_scenario_variability.set_dict['processes_certain_capacity'] == [])
    assert (single_location_scenario_variability.set_dict['processes_varying_capacity'] == [
        'process_deterministic_capacity'])
    assert (
        single_location_scenario_variability.set_dict['processes_uncertain_capacity'] == [])
    assert (single_location_scenario_variability.set_dict['processes_certain_expenditure'] == [
        'process_certain_capacity'])
    assert (
        single_location_scenario_variability.set_dict['processes_varying_expenditure'] == [])
    assert (
        single_location_scenario_variability.set_dict['processes_uncertain_expenditure'] == [])
    assert (
        single_location_scenario_variability.set_dict['processes_segments'] == [])
    assert (
        single_location_scenario_variability.set_dict['locations'] == ['location'])
    assert (
        single_location_scenario_variability.set_dict['materials'] == [])
    assert (
        single_location_scenario_variability.set_dict['process_material_modes'] == [])
    assert (
        single_location_scenario_variability.set_dict['material_modes'] == [])
    assert (
        single_location_scenario_variability.set_dict['sources'] == [])
    assert (
        single_location_scenario_variability.set_dict['sinks'] == [])
    assert (
        single_location_scenario_variability.set_dict['transports'] == [])
    assert (
        single_location_scenario_variability.set_dict['resources_trans'] == [])
