#!/usr/bin/env python
# coding: utf-8

# # Multiscale MILP
# 
# This is a continuation of 'One Location, One Temporal Scale, One Operation, Linear Programming Example' [Example 1]. Refer Example 1 to learn the basics on how Energia models processes. 
# 
# In this example, we add another Process [Solar PV] and Storage [Li-ion Battery]. Technology choice is modeled using binaries. Moreover, the model is multiscale as the operational capacities are decision variables. 

# In[1]:


from energia import *

m = Model('example2')
m.q = Periods()
m.y = 4 * m.q
m.usd = Currency()


# ## Resources

# ### Conveniently declaring components
# 
# Use m.declare(\<Object Type\>, \<list of names\>) to declare a large number of objects in one step.

# In[2]:


m.declare(Resource, ['power', 'wind', 'solar'])


# ### Set bounds on Resource flows
# 
# Unlike wind which has bound on the total consumption, we set a daily limit on solar energy. The same bound is repeated in each quarter. The following constraints are written.
# 
# $\mathbf{cons}_{solar, network, quarter_0} \leq 100$
# 
# $\mathbf{cons}_{solar, network, quarter_1} \leq 100$
# 
# $\mathbf{cons}_{solar, network, quarter_2} \leq 100$
# 
# $\mathbf{cons}_{solar, network, quarter_3} \leq 100$

# In[3]:


m.solar.consume(m.q) <= 100
m.wind.consume <= 400
m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]


# ## Operations 

# ### Capacity as a variable 
# 
# Here we want the optimization problem to determine the optimal capacity. Moreover, we set binaries to avoid the lower bound being adhered to if the process is not set up. 
# 
# If the bounds are meant to be compulsory limits, skip the .x 

# In[4]:


m.wf = Process()
m.wf(m.power) == -1 * m.wind
m.wf.capacity.x <= 100
m.wf.capacity.x >= 10
m.capacity.show()


# Unlike in Example 1, where the capacity was know, capacity is a variable here. 
# 
# Moreover, the expenditure associated with operating and capacitating are different

# In[ ]:





# In[ ]:


m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
m.wf.capacity[m.usd.spend] == 990637 + 3354
m.wf.operate[m.usd.spend] == 49
m.operate.show(True)


# In[ ]:


m.pv = Process()
m.pv(m.power) == -1 * m.solar
m.pv.capacity.x <= 100
m.pv.capacity.x >= 10
m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
m.pv.capacity[m.usd.spend] == 567000 + 872046
m.pv.operate[m.usd.spend] == 90000


# ### Storage Operation
# 
# energia now allows storing to require the use of other resources, example power for hydrogen cryogenic storage. 
# 
# Provide an equation similar to Process, in this case the basis is the stored resource 
# If no other resource is provided, it is assumed to be the charging/discharging efficiency
# 
# Note that the following are created internally: 
# 1. auxilary resource  with name resource.stored 
# 2. charging and discharging processes as storage.charge and storage.discharge 
# 
# The parameters for each of these can be set individually, thus allowing for a wide range of modeling approaches 

# In[ ]:


m.lii = Storage()

m.lii(m.power) == 0.9
m.lii.capacity.x <= 100
m.lii.capacity.x >= 10

# m.lii.capacity >= 10
m.lii.capacity[m.usd.spend] == 1302182 + 41432

m.lii.inventory[m.usd.spend] == 2000
m.lii.charge.capacity <= 100
m.lii.discharge.capacity <= 100


# ## Locating Operations
# 
# Operations can be located as 
# 
# operation.locate(\<list of locations\>)
# 
# or 
# 
# m.location.operations(\<list of operations\>)
# 
# They both do the same thing 

# In[ ]:


m.pv.locate(m.network)
m.network.locate(m.wf, m.lii)


# ## Inventory Balance
# 
# Inventory is passed on from one time period (t - 1) to the next (t) and hence features in the general resource balance for resource.stored 

# 

# In[ ]:


m.inventory.show()


# ## Optimize!

# In[ ]:


m.usd.spend.opt()


# ## Solution

# ### Inventory Profiles
# 
# The inventory maintained in each time period is:

# In[ ]:


m.inventory.output()


# The amount charged into inventory is:

# In[ ]:


m.produce(m.power.lii, m.lii.charge.operate, m.q).output()


# The amount discharged from inventory is:

# In[ ]:


m.produce(m.power, m.lii.discharge.operate, m.q).output()


# ### Integer Decisions 
# 
# All the operations are setup in this case

# In[ ]:


m.capacity.reporting.output()


# In[ ]:


m.capacity.output()

