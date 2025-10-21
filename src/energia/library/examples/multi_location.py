#!/usr/bin/env python
# coding: utf-8

# # Multi Location, Multiple Temporal Scales, Multiple Operations Including Transport, Mixed Integer Linear Programming Example
# 
# ## [Example 4]
# 
# This is a continuation of 'One Location, Multiple Temporal Scales, Multiple Operations, Mixed Integer Linear Programming with Material and Emission Considerations Example' [Example 3]. 
# 
# We update Example 3 to now allow multiple locations and Transport options between them.
# 

# ## From Example 3

# In[1]:


from energia import *

m = Model('example4')
m.q = Periods()
m.y = 4 * m.q
m.usd = Currency()


# In[2]:


m.periods


# ## Declaring Locations 

# In[3]:


m.ho = Location(label='Houston')
m.sd = Location(label='San Diego')
m.ny = Location(label='New York')
# m.usa = m.ho + m.sd + m.ny


# In[4]:


m.locations


# ### The Network 
# 
# Given that we have not used a nested set of locations, a network is made:

# In[5]:


m.network


# This network contains the three locations at (ho, sd, ny)

# In[6]:


m.network.has


# 

# ## General Bounds Default to Network

# In[7]:


m.declare(Resource, ['power', 'wind', 'solar'])
# m.solar.consume == True
# m.wind.consume == True
m.solar.consume <= 1200
m.wind.consume <= 1200
# m.consume.show()


# ## Location-specific Bounds 
# 
# Spatial specificity can be provided along with temporal fidelity. 
# In the example below, the temporal fidelity is implied since the data has 4 samples.
# 
# Note that an individual general resource balance is generated for power at each location

# In[8]:


m.power.release(m.ho).prep(30) >= [0.6, 0.7, 0.8, 0.3]
m.power.release(m.sd).prep(100) >= [0.4, 0.9, 0.7, 0.6]
m.power.release(m.ny).prep(180) >= [0.2, 0.5, 0.7, 0.5]
m.release.show()


# ## For All Locations 
# 
# Generally, in Energia to repeat a constraint over a set, use .forall()
# 
# If a list is provided, the bounds are iterated over the list [see LB cons]
# else the bounds are repeated [see UB cons]

# In[9]:


m.wf = Process(m.power)
m.wf(m.power) == -1 * m.wind
[10, 7, 20] <= m.wf.capacity.x.forall(m.network.has)
m.wf.capacity.x.forall(m.network.has) <= 100
m.wf.show()


# Bounds can also be provided individually

# In[10]:


m.wf.operate.prep(norm=True)(m.ho) <= [0.9, 0.8, 0.5, 0.7]
m.wf.operate.prep(norm=True)(m.sd) <= [0.8, 0.7, 0.6, 0.5]
m.wf.operate.prep(norm=True)(m.ny) <= [0.6, 0.5, 0.4, 0.3]
m.operate.show(True)
# m.wf.operate.prep(norm = True).forall(m.network.has) <= [[0.9, 0.8, 0.5, 0.7], [0.8, 0.7, 0.6, 0.5], [0.6, 0.5, 0.4, 0.3]]


# Calculations can also be provided for all locations as a list or repeated

# In[11]:


m.wf.capacity[m.usd.spend].forall(m.network.has) == [90000, 70000, 60000]
m.wf.operate[m.usd.spend] == 49


# In the case where location specific data is not provided, the parameter is assumed tuo apply to the network

# In[12]:


m.pv = Process()
m.pv(m.power) == -1 * m.solar


# In[13]:


m.pv.capacity.x <= 100
m.pv.capacity.x >= 10
m.pv.operate.prep(norm=True).forall(m.network.has) <= [
    [0.6, 0.8, 0.9, 0.7],
    [0.5, 0.7, 0.6, 0.5],
    [0.4, 0.6, 0.5, 0.4],
]
m.pv.capacity[m.usd.spend] == 567000 + 872046
m.pv.operate[m.usd.spend] == 90000

m.lii = Storage()
m.lii(m.power) == 0.9
m.lii.capacity.x <= 100
m.lii.capacity.x >= 10
m.lii.capacity[m.usd.spend] == 1302182 + 41432
m.lii.inventory[m.usd.spend] == 2000
m.lii.charge.capacity <= 100
m.lii.charge.operate <= 1
m.lii.discharge.capacity <= 100
m.lii.discharge.operate <= 1

m.gwp = Environ()

m.wf.capacity[m.gwp.emit] == 1000
m.pv.capacity[m.gwp.emit] == 2000
m.lii.capacity[m.gwp.emit] == 3000

m.cement = Material()
m.cement.consume <= 1000000
m.cement.consume[m.usd.spend] == 17
m.cement.consume[m.gwp.emit] == 0.9

m.wf.capacity[m.cement.use] == 400
m.pv.capacity[m.cement.use] == 560
m.lii.capacity[m.cement.use] == 300


# ## Linkages 

# A grid of valid linkages can be created from sources to sinks.
# 
# Linkages are always one directional, stating bi, created a link from source to sink and the other way round 
# 
# If multiple links exist between two locations with different distances, it is necessary to create named links. 
# Again, it needs to be stated whether the links are bi directional 

# In[14]:


m.Link(source=m.ho, sink=m.sd, dist=2000, bi=True)
# m.Link(source = m.sd, sink=m.ny, dist = 1500)
m.road = Linkage(source=m.ho, sink=m.ny, dist=3000, bi=True)
# m.rail = Link(source = m.ho, sink=m.ny, dist = 5000, bi = True)
m.linkages


# In[15]:


m.ho.links(m.sd)


# ## Transits
# 
# Declare some transport options between across the linkages 
# 

# In[16]:


# m.declare(Resource, ['h2o', 'co2'])
# m.grid = Transport()
# m.grid(m.power) == -m.h2o + m.co2
# m.grid.capacity.x.forall([m.ho - m.sd, m.road]) <= 100
# m.grid.operate.prep(norm=True).forall([m.ho - m.sd, m.road]) <= [
#     [0.9, 0.8, 0.5, 0.7],
#     [0.8, 0.7, 0.6, 0.9],
# ]
# m.grid.operate[m.usd.spend] == 2000
# m.grid.capacity[m.usd.spend] == 1000


# In[17]:


m.ho.locate(m.pv, m.wf, m.lii)
m.sd.locate(m.pv, m.wf, m.lii)
m.ny.locate(m.pv, m.wf, m.lii)


# In[ ]:


m.inventory.show()


# In[ ]:


m.solar.show()


# In[18]:


m.spend.show()


# In[19]:


m.maps


# In[20]:


m.show()


# In[22]:


m.show(category='Mapping')


# In[23]:


m.usd.spend.opt()

