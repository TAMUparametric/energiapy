#!/usr/bin/env python
# coding: utf-8

# # mpLP reformulation of an energy systems MILP

# 
# \begin{equation}
#     min \sum_{t \in \mathcal{T}^{net}} \sum_{p \in \mathcal{P}} Capex_{p,t} \times Cap^P_{p,t} + \sum_{t \in \mathcal{T}^{sch}} \sum_{r \in \mathcal{R}^{cons}}  Price_{r,t}  \times C_{r,t} + \sum_{t \in \mathcal{T}^{sch}} \sum_{p \in \mathcal{P}}  Vopex_{r,t} \times P_{r,t} 
# \end{equation}
# 
# 
# \begin{equation}
#     Cap^S_{r,t} \leq Cap^{S-max}_{r,t} \times X^S_{r,t} \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}^{net}
# \end{equation}
# 
# \begin{equation}
#     Cap^P_{p,t} \leq Cap^{P-max}_{p,t} \times X^P_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}^{net}
# \end{equation} 
# 
# \begin{equation}
#     P_{p,t} \leq Cap^{P}_{p,t}  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}^{sch}
# \end{equation} 
# 
# \begin{equation}
#     Inv_{r,t} \leq Cap^{S}_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}^{sch}
# \end{equation} 
# 
# 
# \begin{equation}
#     - S_{r,t} \leq - D_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}^{sch}
# \end{equation}
# 
# \begin{equation}
#     C_{r,t} \leq C^{max}_{r,t} \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}^{sch}
# \end{equation}
# 
# 
# \begin{equation}
#     - S_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}, t \in \mathcal{T}^{sch}
# \end{equation}
# 
# \begin{equation}
#     -Inv_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}, t \in \mathcal{T}^{sch}
# \end{equation}
# 
# \begin{equation}
#     \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) + C_{r,t} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}, t \in \mathcal{T}^{sch}
# \end{equation}
# 
# \begin{equation}
#     S_{r,t}, C_{r,t}, Inv_{r,t}, P_{p,t}, Cap^P_p, Cap^S_r \in R_{\geq 0}
# \end{equation}
# 
# 
# 

# ## mpLP reformulation

# Reformulated as an mpLP

# 
# \begin{equation}
#     min \hspace{1cm} \sum_{p \in \mathcal{P}} Capex_p \times \epsilon_p \times P_p + \sum_{r \in \mathcal{R}^{cons}} C_r \times \gamma_r 
# \end{equation}
# 
# 
# \begin{equation}
#     Inv_r \leq Cap^{S-max}_r \hspace{1cm} \forall r \in \mathcal{R}^{stored}
# \end{equation}
# 
# \begin{equation}
#     - S_r \leq - D_r \times \beta_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
# \end{equation}
# 
# \begin{equation}
#     C_r \leq C^{max}_r \times \delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons} 
# \end{equation}
# 
# \begin{equation}
#     P_p \leq Cap^{P-max}_p \times \alpha_p \hspace{1cm} \forall p \in \mathcal{P}
# \end{equation} 
# 
# \begin{equation}
#     - S_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}
# \end{equation}
# 
# \begin{equation}
#     - Inv_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}
# \end{equation}
# 
# \begin{equation}
#     \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) + C_{r} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}
# \end{equation}
# 
# \begin{equation}
#     \alpha_p \in A_p \hspace{1cm} \forall p \in \mathcal{P}
# \end{equation}
# 
# \begin{equation}
#     \beta_r \in B_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
# \end{equation}
# 
# \begin{equation}
#     \gamma_r \in \Gamma_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
# \end{equation}
# 
# \begin{equation}
#     \delta_r \in \Delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
# \end{equation}
# 
# \begin{equation}
#     \epsilon_p \in E_p \hspace{1cm} \forall p \in \mathcal{P}
# \end{equation}
# 
# 
# \begin{equation}
#     S_r, C_r, Inv_r, P_p \in R_{\geq 0}
# \end{equation}
# 

# ## Example Problem

# 
# \begin{equation}
#     p \in \{LI_c, LI_d, WF, PV\} 
# \end{equation}
# 
# 
# \begin{equation}
#     r \in \{charge, power, wind, solar\} 
# \end{equation}
# 

# 
# \begin{equation}
#     min \hspace{1cm} \left[\begin{matrix}1302\\0\\990\\567\end{matrix}\right]^T \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right]
# \end{equation}
# 

# 
# \begin{equation}
#     I_3\left[\begin{matrix}Inv_{charge}\\C_{wind}\\C_{solar}\\P_{LI_c}\\P_{LI_d}\end{matrix}\right] \leq \left[\begin{matrix} 100\\100\\100\\100\\100\end{matrix}\right]
# \end{equation}
# 

# 
# \begin{equation}
#     I_3\left[\begin{matrix}-S_{power}\\P_{WF}\\P_{PV}\end{matrix}\right] \leq \left[\begin{matrix}-300 & 0 & 0\\0 & 100 & 0\\0 & 0 & 100\end{matrix}\right] \left[\begin{matrix}\beta_{power}\\ \alpha_{WF}\\\alpha_{PV}\end{matrix}\right]
# \end{equation}
# 

# 
# \begin{equation}
#     I_4\left[\begin{matrix} - Inv_{charge} \\ -S_{power} \\ C_{wind} \\ C_{solar} \end{matrix}\right] + \left[\begin{matrix}0.89 & -1 & 0 & 0\\-1 & 1 & 0.85 & 0.75\\0 & 0 & -1 & 0\\0 & 0 & 0 & -1\end{matrix}\right] \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right] = 0
# \end{equation}
# 

# 
# \begin{equation}
#     \alpha_p \in \mathcal{A}_p \hspace{1cm} \forall p \in \{WF, PV\} 
# \end{equation}
# 
# \begin{equation}
#     \beta_r \in \mathcal{B}_r \hspace{1cm} \forall r \in \{Power\} 
# \end{equation}

# $\textbf{Import modules}$

# In[1]:


from energia import *

m = Model(init=[si_units])


# In[2]:


m.solar = Resource(basis=m.MW, label='Solar Power')
m.solar.consume <= 100
m.wind = Resource(basis=m.MW, label='Wind Power')
m.wind.consume <= 100
m.power = Resource(basis=m.MW, label='Power generated')
m.power.release == (120, 150)


# In[3]:


m.lii = Storage()

m.lii(m.power) == 0.9
m.power.lii.inventory == (10, 100)

# m.lii.capacity >= 10
# m.lii.capacity[m.money.spend] == 1302
m.power.lii.inventory[m.money.spend] == 2000
m.lii.charge.operate <= 25
m.lii.discharge.operate <= 25


# In[4]:


m.wf = Process()
m.wf(m.power) == -1 / 0.85 * m.wind
# m.wf.operate == (0, 100)
m.wf.operate <= 100
m.wf.operate[m.money.spend] == 990

m.pv = Process()
m.pv(m.power) == -1 / 0.75 * m.solar
# m.pv.operate == (0, 100)
m.pv.operate <= 100
m.pv.operate[m.money.spend] == 567


# In[5]:


m.locate(m.pv, m.wf, m.lii)


# In[6]:


m.money.spend.obj()
m.solve()

m.money.spend.opt()


# In[7]:


m.eval(120, 100)


# In[8]:


m.draw()


# In[9]:


p = m.program

p.variables[0]


# In[10]:


# coordinates = []
# from itertools import product

# for i, j, k in product(
#     numpy.linspace(0, 1, 50), numpy.linspace(0, 1, 50), numpy.linspace(0, 1, 50)
# ):
#     l = solution.evaluate_objective(numpy.array([[i], [j], [k]]))
#     if l is not None:
#         coordinates.append((i, j, k, l[0][0]))


# Unique solutions

# In[11]:


# set([coordinates[i][3] for i in range(len(coordinates))])


# In[12]:


# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib import cm

# # Sample data: (x, y, z, color_value)
# data = coordinates
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# x_vals, y_vals, z_vals, color_vals = zip(*data)

# # Use color map to convert the color_value to a color
# norm = plt.Normalize(min(color_vals), max(color_vals))
# colors = cm.viridis(norm(color_vals))

# scatter = ax.scatter(x_vals, y_vals, z_vals, c=colors, cmap='viridis', s=50)

# # Add a color bar to show the mapping of color values
# cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
# cbar.set_label('Fourth Dimension')

# # ax.set_ylim(ax.get_xlim()[::-1])
# # ax.set_ylim(ax.get_ylim()[::-1])
# # ax.set_ylim(ax.get_zlim()[::-1])

# ax.zorder = 0
# ax.set_xlim(0, 1)
# ax.set_ylim(0, 1)
# ax.set_zlim(0, 1)

# ax.set_xlabel('X Label')
# ax.set_ylabel('Y Label')
# ax.set_zlabel('Z Label')
# plt.show()


# In[13]:


# coordinates = [tuple(map(lambda x: 0 if x < 0.001 else x, i)) for i in coordinates]


# In[14]:


m = Model(init=[si_units])
m.solar = Resource(basis=m.MW, label='Solar Power')
m.solar.consume <= 100
m.wind = Resource(basis=m.MW, label='Wind Power')
m.wind.consume <= 100
m.power = Resource(basis=m.MW, label='Power generated')
m.power.release == (56, 60)
m.h2o = Resource(basis=m.kg, label='Water')
m.h2o.consume <= 500
m.o2 = Resource(basis=m.kg, label='Oxygen')
m.o2.release == True

m.h2 = Resource(basis=m.kg, label='Hydrogen')
m.h2.release == (0, 80)


m.ur = Resource(basis=m.kg, label='Uranium')
m.ur.consume <= 1000
m.ur.consume[m.money.spend] == 42.70 / (250 / 2)

m.wf = Process()
m.wf(m.power) == -1 / 0.85 * m.wind
# m.wf.operate == (0, 100)
m.wf.operate == (0, 100)
m.wf.operate[m.money.spend] == 990

m.pv = Process()
m.pv(m.power) == -1 / 0.75 * m.solar
# m.pv.operate == (0, 100)
m.pv.operate == (0, 100)
m.pv.operate[m.money.spend] == 567


m.lii = Storage()

m.lii(m.power) == 0.89
m.power.lii.inventory <= 200

m.lii.charge.operate <= 25
m.lii.discharge.operate <= 25

m.lii.charge.operate[m.money.spend] == 1302


m.pem = Process(
    basis=m.kg,
    label='PEM Electrolyzer',
)
m.pem(-m.power) == 0.3537 * m.h2 - 3.1839 * m.h2o + m.o2
m.pem.operate <= 100
m.pem.operate[m.money.spend] == 1550

m.asmr = Process(
    basis=m.MW,
    label='Small Modular Reactor (SMR)',
)
m.asmr(m.power) == -4.17e-5 * m.ur - 3.364 * m.h2o + m.power
m.asmr.operate <= 100
m.asmr.operate[m.money.spend] == 7988951

m.locate(m.pv, m.wf, m.lii, m.pem, m.asmr)

m.money.spend.obj()


# In[15]:


m.solve()


# In[16]:


len(m.solution[0].critical_regions)


# In[17]:


m = Model(init=[si_units])
m.solar = Resource(basis=m.MW, label='Solar Power')
m.solar.consume <= 100
m.wind = Resource(basis=m.MW, label='Wind Power')
m.wind.consume <= 100
m.power = Resource(basis=m.MW, label='Power generated')
m.power.release <= 60
m.h2o = Resource(basis=m.kg, label='Water')
m.h2o.consume <= 500
m.o2 = Resource(basis=m.kg, label='Oxygen')
m.o2.release == True

m.h2 = Resource(basis=m.kg, label='Hydrogen')
m.h2.release >= 2


m.ur = Resource(basis=m.kg, label='Uranium')
m.ur.consume <= 1000
m.ur.consume[m.money.spend] == 42.70 / (250 / 2)

m.wf = Process()
m.wf(m.power) == -1 / 0.85 * m.wind
m.wf.operate <= 100
m.wf.operate[m.money.spend] == 990

m.pv = Process()
m.pv(m.power) == -1 / 0.75 * m.solar
m.pv.operate <= 100
m.pv.operate[m.money.spend] == 567


m.lii = Storage()

m.lii(m.power) == 0.89
m.power.lii.inventory <= 200

m.lii.charge.operate <= 25
m.lii.discharge.operate <= 25

m.lii.charge.operate[m.money.spend] == 1302


m.pem = Process(
    basis=m.kg,
    label='PEM Electrolyzer',
)
m.pem(-m.power) == 0.3537 * m.h2 - 3.1839 * m.h2o + m.o2
m.pem.operate <= 100
m.pem.operate[m.money.spend] == 1550

m.asmr = Process(
    basis=m.MW,
    label='Small Modular Reactor (SMR)',
)
m.asmr(m.power) == -4.17e-5 * m.ur - 3.364 * m.h2o + m.power
m.asmr.operate <= 100
m.asmr.operate[m.money.spend] == 7988951

m.locate(m.pv, m.wf, m.lii, m.pem, m.asmr)

# m.money.spend.obj()

m.money.spend.opt()


# In[18]:


m.draw(m.operate)

