from src.energiapy.components.resource import Resource
from src.energiapy.components.process import Process, ProcessMode, CostDynamics

def test_process_multiconv():
    Resource1 = Resource(name = 'resource1')
    Resource2 = Resource(name = 'resource2')    
    Process_multi = Process(name = 'process_multi', conversion= {0: {Resource1: -1, Resource2:2}, 1:{Resource1: -1, Resource2:2.5}})
    assert Process_multi.processmode == ProcessMode.multi


def test_process_storage_mode():
    Resource1 = Resource(name = 'resource1')  
    Process_storage = Process(name = 'process_storage', storage= Resource1)
    assert Process_storage.process_mode == ProcessMode.storage
    
def test_process_storage_storemax(): 
    Resource1 = Resource(name = 'resource1')  
    Process_storage = Process(name = 'process_storage', storage= Resource1, store_max= 100)
    assert Process_storage.resource_storage.store_max == 100
    
   
def test_process_cost_dynamics(): 
    Resource1 = Resource(name = 'resource1')  
    Process_pwl = Process(name = 'process_storage', capex= {i: i+1 for i in range(4)})
    assert Process_pwl.cost_dynamics == CostDynamics.pwl
    

    
     

