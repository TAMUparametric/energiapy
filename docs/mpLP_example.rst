Reformulating an energy systems MILP as a mpLP 
==============================================

In this example a simple multi-scale energy systems MILP is reformulated as a single-period mpLP

**Nomenclature**

The sets and variables used are stated here

*Sets*


- R - set of all resources r
- P - set of all processes p
- T - set of temporal periods p


*Subsets*

- R\ :sup:`storage` - set of resources that can be stored
- R\ :sup:`sell` - set of resources that can be discharged
- R\ :sup:`demand` - set of resources that meet  demand
- R\ :sup:`cons` - set of resources that can be consumed
- P\ :sup:`uncertain` - set of processes with uncertain capacity
- T - set of temporal periods 
- T\ :sup:`net` - set of temporal periods t for network level decision making
- T\ :sup:`sch` - set of temporal periods t for schedule level decision making


*Continuous Variables*


- P\ :sub:`p,t` - production level of p :math:`{\in}`  P in time period t :math:`{\in}` T\ :sup:`sch`  
    
- C\ :sub:`r,t` - consumption of r :math:`{\in}` R\ :sup:`cons` time period t :math:`{\in}` T\ :sup:`sch` 
    
- S\ :sub:`r,t` - discharge of r :math:`{\in}` R\ :sup:`demand` time period t :math:`{\in}` T\ :sup:`sch` 
    
- Inv\ :sub:`r,t` - inventory level of r :math:`{\in}` R\ :sup:`storage`  in time period t :math:`{\in}` T\ :sup:`sch`
    
- Cap\ :sup:`S` \ :sub:`r,t` - installed inventory capacity for resource r :math:`{\in}`  R\ :sup:`storage` in time period t :math:`{\in}` T\ :sup:`net`
    
- Cap\ :sup:`P` \ :sub:`p,t` - installed production capacity for process p :math:`{\in}` P in time period t :math:`{\in}` T\ :sup:`net`
    



*Binary Variables*


- X\ :sup:`P` \ :sub:`p,t` - network binary for production process p :math:`{\in}` P in time period t :math:`{\in}` T\ :sup:`net`
- X\ :sup:`S` \ :sub:`r,t` - network binary for inventory of resource r :math:`{\in}` R\ :sup:`storage` in time period t :math:`{\in}` T\ :sup:`net`



*Parametric Variables*


- :math:`{\\alpha}` \ :sub:`p` - uncertainty in production capacity of process p :math:`{\in}` P\ :sup:`uncertain`
- :math:`{\\beta}` \ :sub:`r` - uncertainty in demand for resource r :math:`{\in}` R\ :sup:`demand`
- :math:`{\\gamma}` \ :sub:`r` - uncertainty in purchase price for resource r :math:`{\in}` R\ :sup:`cons`
- :math:`{\\delta}` \ :sub:`r` - uncertainty in consumption availability for resource r :math:`{\in}` R\ :sup:`demand`


*Parameters*


- Cap\ :sup:`P-max` \ :sub:`p,t` - maximum production capacity of process p :math:`{\in}` P in time period t :math:`{\in}` T\ :sup:`net`
- Cap\ :sup:`S-max` \ :sub:`r,t` - maximum inventory capacity for process r :math:`{\in}` R\ :sup:`storage` in time period t :math:`{\in}` T\ :sup:`net`
- Capex\ :sub:`p,t` - capital expenditure for process p :math:`{\in}` P in time t :math:`{\in}` T\ :sup:`net`
- Price\ :sub:`r,t` - purchase price for resource r :math:`{\in}` R\ :sup:`cons` in time t :math:`{\in}` T\ :sup:`sch`
- C\ :sup:`max` \ :sub:`r,t` - maximum consumption availability for resource r :math:`{\in}` R\ :sup:`cons` in time t :math:`{\in}` T\ :sup:`sch`
- D\ :sub:`r,t` - demand for resource r in R\ :sup:`sell` in time t :math:`{\in}` T\ :sup:`sch`

**MILP Formulation**

Given is a general MILP modeling and optimization framework for simultaneous network design and scheduling.


.. math::
    \begin{equation}
        min \sum_{t \in \mathcal{T}^{net}} \sum_{p \in \mathcal{P}} Capex_{p,t} \times Cap^P_{p,t} + \sum_{t \in \mathcal{T}^{sch}} \sum_{r \in \mathcal{R}^{cons}}  Price_{r,t}  \times C_{r,t} + \sum_{t \in \mathcal{T}^{sch}} \sum_{p \in \mathcal{P}}  Vopex_{r,t} \times P_{r,t} 
    \end{equation}


.. math::
    \begin{equation}
        Cap^S_{r,t} \leq Cap^{S-max}_{r,t} \times X^S_{r,t} \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}^{net}
    \end{equation}

.. math::
    \begin{equation}
        Cap^P_{p,t} \leq Cap^{P-max}_{p,t} \times X^P_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}^{net}
    \end{equation} 

.. math::
    \begin{equation}
        P_{p,t} \leq Cap^{P}_{p,t}  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}^{sch}
    \end{equation} 

.. math::
    \begin{equation}
        Inv_{r,t} \leq Cap^{S}_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}^{sch}
    \end{equation} 


.. math::
    \begin{equation}
        - S_{r,t} \leq - D_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}^{sch}
    \end{equation}

.. math::
    \begin{equation}
        C_{r,t} \leq C^{max}_{r,t} \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}^{sch}
    \end{equation}

.. math::
    \begin{equation}
        - S_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}, t \in \mathcal{T}^{sch}
    \end{equation}

.. math::
    \begin{equation}
        -Inv_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}, t \in \mathcal{T}^{sch}
    \end{equation}

.. math::
    \begin{equation}
        \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) + C_{r,t} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}, t \in \mathcal{T}^{sch}
    \end{equation}

.. math::
    \begin{equation}
        S_{r,t}, C_{r,t}, Inv_{r,t}, P_{p,t}, Cap^P_p, Cap^S_r \in R_{\geq 0}
    \end{equation}

**mpLP**

Reformulated, a general mpLP for the above MILP will looks something like this:

.. math::     
    \begin{equation}
        min \hspace{1cm} \sum_{p \in \mathcal{P}} Capex_p \times P_p + \sum_{r \in \mathcal{R}^{cons}} C_r \times \gamma_r 
    \end{equation}

.. math::
    \begin{equation}
        Inv_r \leq Cap^{S-max}_r \hspace{1cm} \forall r \in \mathcal{R}^{stored}
    \end{equation}

.. math::
    \begin{equation}
        - S_r \leq - D_r \times \beta_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
    \end{equation}

.. math::
    \begin{equation}
        C_r \leq C^{max}_r \times \delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons} 
    \end{equation}

.. math::
    \begin{equation}
        P_p \leq Cap^{P-max}_p \times \alpha_p \hspace{1cm} \forall p \in \mathcal{P}
    \end{equation} 

.. math::
    \begin{equation}
        - S_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}
    \end{equation}

.. math::
    \begin{equation}
        -Inv_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}
    \end{equation}

.. math::
    \begin{equation}
        \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) + C_{r} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

.. math::
    \begin{equation}
        \alpha_p \in A_p \hspace{1cm} \forall p \in \mathcal{P}
    \end{equation}

.. math::
    \begin{equation}
        \beta_r \in B_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
    \end{equation}

.. math::
    \begin{equation}
        \gamma_r \in \Gamma_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

.. math::
    \begin{equation}
        \delta_r \in \Delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

.. math::
    \begin{equation}
        S_r, C_r, Inv_r, P_p \in R_{\geq 0}
    \end{equation}

**Example energiapy implementation**

Let us now look at an example problem


.. math::
    \begin{equation}
        p \in \{LI_c, LI_d, WF, PV\} 
    \end{equation}

.. math::
    \begin{equation}
        r \in \{charge, power, wind, solar\} 
    \end{equation}

.. math::
    \begin{equation}
        min \hspace{1cm} \left[\begin{matrix}1302\\0\\990\\567\end{matrix}\right]^T \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right]
    \end{equation}

.. math::
    \begin{equation}
        I_3\left[\begin{matrix}Inv_{charge}\\C_{wind}\\C_{solar}\\P_{LI_c}\\P_{LI_d}\end{matrix}\right] \leq \left[\begin{matrix} 100\\100\\100\\100\\100\end{matrix}\right]
    \end{equation}

.. math::
    \begin{equation}
        I_3\left[\begin{matrix}-S_{power}\\P_{WF}\\P_{PV}\end{matrix}\right] \leq \left[\begin{matrix}-300 & 0 & 0\\0 & 100 & 0\\0 & 0 & 100\end{matrix}\right] \left[\begin{matrix}\beta_{power}\\ \alpha_{WF}\\\alpha_{PV}\end{matrix}\right]
    \end{equation}

.. math::
    \begin{equation}
        I_4\left[\begin{matrix} - Inv_{charge} \\ -S_{power} \\ C_{wind} \\ C_{solar} \end{matrix}\right] + \left[\begin{matrix}0.89 & -1 & 0 & 0\\-1 & 1 & 0.85 & 0.75\\0 & 0 & -1 & 0\\0 & 0 & 0 & -1\end{matrix}\right] \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right] = 0
    \end{equation}

.. math::
    \begin{equation}
        \alpha_p \in \mathcal{A}_p \hspace{1cm} \forall p \in \{WF, PV\} 
    \end{equation}

.. math::
    \begin{equation}
        \beta_r \in \mathcal{B}_r \hspace{1cm} \forall r \in \{Power\} 
    \end{equation}


Now we are ready to implement the above problem in energiapy

**Import modules**

.. code-block:: python

    from energiapy.components.temporal_scale import Temporal_scale
    from energiapy.components.resource import Resource, VaryingResource
    from energiapy.components.process import Process, VaryingProcess
    from energiapy.components.location import Location
    from energiapy.components.scenario import Scenario
    from energiapy.components.result import Result 
    from energiapy.model.formulate import formulate, Constraints, Objective
    from energiapy.plot import plot
    from energiapy.model.solve import solve
    import numpy
    from ppopt.mpqp_program import MPQP_Program
    from ppopt.mplp_program import MPLP_Program
    from ppopt.mp_solvers.solve_mpqp import solve_mpqp, mpqp_algorithm
    from ppopt.plot import parametric_plot

**Define the temporal scale**

In the mpLP example, instead of using multi-scale indices, the problem can be formulated in a single period.

.. code-block:: python

    scales = Temporal_scale(discretization_list=[1])

**Declare the problem scenario**

.. code-block:: python

    Solar = Resource(name='Solar', cons_max=100, basis='MW', label='Solar Power')

    Wind = Resource(name='Wind', cons_max= 100, basis='MW', label='Wind Power')

    Power = Resource(name='Power', basis='MW', demand = True, label='Power generated', varying= VaryingResource.uncertain_demand)

    LiI = Process(name='LiI', storage= Power, capex = 1302, fopex= 0, vopex = 0,  prod_max=50, storage_loss = 0.11,  label='Lithium-ion battery', basis = 'MW')

    WF = Process(name='WF', conversion={Wind: -1, Power: 0.85},capex=990, fopex= 0, vopex=0, prod_max=100, label='Wind mill array', basis = 'MW', varying =  VaryingProcess.uncertain_capacity)

    PV = Process(name='PV', conversion={Solar: -1, Power: 0.75}, capex=567, fopex=0, vopex=0, prod_max=100, label = 'Solar PV', basis = 'MW', varying = VaryingProcess.uncertain_capacity)
    
    region = Location(name='region', processes= {LiI, PV, WF}, scales=scales, label='some region')
    
    example = Scenario(name= 'example', demand = {region: {Power: 100}}, network= region, scales= scales, label= 'example scenario')


**Generate the problem in matrix form**

.. code-block:: python

    A, b, c, H, CRa, CRb, F  = example.matrix_form()


**Solve the problem using the ppopt solver**

.. code-block:: python

    prog = MPLP_Program(A, b, c, H, CRa, CRb, F, equality_indices=[0,1,2,3])
    prog.solver.solvers['lp'] = 'gurobi'
    prog.warnings()
    prog.display_warnings()
    solution1 = solve_mpqp(prog, mpqp_algorithm.combinatorial)
