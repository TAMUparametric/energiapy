#!/usr/bin/env python
# coding: utf-8

# # Multiscale MILP with Materials and Emission
# 
# This is a continuation of 'One Location, Multiple Temporal Scales, Multiple Operations, Mixed Integer Linear Programming Example' [Example 2]. 
# 
# We will be adding the following considerations: 
# 
# 1. material for the establishment of operations 
# 2. global warming potential induced as a sum of our decisions and choices 

# ## See Example 2

# In[14]:


from energia import *

m = Model('example3')
m.q = Periods()
m.y = 4 * m.q


# In[15]:


m.usd = Currency()
m.declare(Resource, ['power', 'wind', 'solar'])
m.solar.consume(m.q) <= 100
m.wind.consume <= 400
m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

m.wf = Process()
m.wf(m.power) == -1 * m.wind
m.wf.capacity.x <= 100
m.wf.capacity.x >= 10
m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
m.wf.capacity[m.usd.spend] == 990637 + 3354
m.wf.operate[m.usd.spend] == 49

m.pv = Process()
m.pv(m.power) == -1 * m.solar
m.pv.capacity.x <= 100
m.pv.capacity.x >= 10
m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
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


# ## Indicator Stream 
# 
# Indicators scale the impact of some decision or flow and project it only a common dimension allowing the calculation of overall impact as a single metric value
# 
# In this case, we consider global warming potential (GWP).

# In[16]:


m.gwp = Environ()


# Now say that we want to consider the impact of setting up operations (specific to the act of construction)
# 
# These can be provided as calculations 

# In[17]:


m.wf.capacity[m.gwp.emit] == 1000
m.pv.capacity[m.gwp.emit] == 2000
m.lii.capacity[m.gwp.emit] == 3000
m.emit.show()


# Note that impact streams are mapped across scales but not balanced, unless a negative (relatively) impact is also assessed! In the case of emission, this would be abatement.

# ## Material Stream
# 
# Note that all the objects found in energia.components.commodity.misc are still resources (Land, Material, etc.)
# 
# This will allow for the modeling of an expansive type of processes.
# 
# Examples:
# 
# 1. land clearance to transform agricultural land into industrial, or land remediation 
# 2. resource intense material recycling 
# 3. some resource flowing being treated as emission flows 
# 
# The possibilities are vast... The advanced modeler may prefer to use Resource() for everything [see Resource Task Network (RTN) Framework]
# 
# In the following example, we consider a limit to cement consumption, as also an expense and gwp impact associated with it

# In[18]:


m.cement = Material()
m.cement.consume <= 1000000
m.cement.consume[m.usd.spend] == 17
m.cement.consume[m.gwp.emit] == 0.9


# Next, we provide details of the use of cement across all operations 

# In[19]:


m.wf.capacity[m.cement.use] == 400
m.pv.capacity[m.cement.use] == 560
m.lii.capacity[m.cement.use] == 300


# Material use is summed up across all operations, and adheres to an upper bound in terms of consumption. 

# In[20]:


m.cement.show()


# GWP impact is now the sum of impact from material use as well as constuction 

# In[21]:


m.emit.show()


# ## Locate Operations

# In[22]:


m.network.locate(m.wf, m.pv, m.lii)


# ## Optimization 
# 
# Let us minimize GWP this time. Note that m.usd.spend.opt() can still be used!

# In[23]:


m.gwp.emit.opt()


# In[24]:


len(m.variables)


# In[25]:


m.show()


# In[26]:


m.output(False)

