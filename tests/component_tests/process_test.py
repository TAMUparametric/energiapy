# , process_multiple_modes
from tests.test_fixtures import process_material_modes, process_storage
from src.energiapy.components.process import MaterialMode, ProcessMode, VaryingProcess


def test_process_material_modes(process_material_modes):
    assert (process_material_modes.resource_req == {'Resource1', 'Resource2'})
    assert (process_material_modes.material_modes == {'Mode1', 'Mode2'})
    assert (process_material_modes.capacity_segments == ['Mode1', 'Mode2'])
    assert (process_material_modes.capex_segments == [2000, 1000])
    assert (process_material_modes.materialmode == MaterialMode.MULTI)
    assert (process_material_modes.processmode == ProcessMode.MULTI)


def test_process_storage(process_storage):
    assert (process_storage.conversion == {
            process_storage.storage: -1, process_storage.resource_storage: 1})
    assert (process_storage.processmode == ProcessMode.STORAGE)
    assert (process_storage.resource_req == {
            'Process1_Resource1_stored', 'Resource1'})
    assert (process_storage.conversion_discharge == {
            process_storage.storage: 0.99, process_storage.resource_storage: -1})


# def test_process_multiple_modes(process_multiple_modes):
#     assert (VaryingProcess.MULTIMODE in process_multiple_modes.varying)
#     assert (process_multiple_modes.processmode == ProcessMode.MULTI)
