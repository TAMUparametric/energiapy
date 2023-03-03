Reformulating an energy systems MILP as a mpLP 
==============================================

In this example a simple multi-scale energy systems MILP is reformulated as a single-period mpLP

**Nomenclature**

The sets and variables used are stated here

.. math::

        
    $\textbf{Sets}$


    - $\mathcal{R}$ - set of all resources r
    - $\mathcal{P}$ - set of all processes p
    - $\mathcal{T}$ - set of temporal periods p


    $\textbf{Subsets}$


    - $\mathcal{R}^{storage}$ - set of resources that can be stored
    - $\mathcal{R}^{sell}$ - set of resources that can be discharged
    - $\mathcal{R}^{demand}$ - set of resources that meet  demand
    - $\mathcal{R}^{cons}$ - set of resources that can be consumed
    - $\mathcal{P}^{uncertain}$ - set of processes with uncertain capacity
    - $\mathcal{T}$ - set of temporal periods p



    $\textbf{Continuous Variables}$


    - $P_{p,t}$ - production level of p $\in$  $\mathcal{P}$ in time period t $\in$ $\mathcal{T}$  
        
    - $C_{r,t}$ - consumption of r $\in$ in $\mathcal{R}^{cons}$ time period t $\in$ $\mathcal{T}$ 
        
    - $S_{r,t}$ - discharge of r $\in$ in $\mathcal{R}^{demand}$ time period t $\in$ $\mathcal{T}$ 
        
    - $Inv_{r,t}$ - inventory level of r $\in$ $\mathcal{R}^{storage}$  in time period t $\in$ $\mathcal{T}$
        
    - $Cap^S_{r}$ - installed inventory capacity for resource r $\in$  $\mathcal{R}^{storage}$ 
        
    - $Cap^P_{p}$ - installed production capacity for process p $\in$ $\mathcal{P}$
        



    $\textbf{Binary Variables}$


    - $X^P_{p}$ - network binary for production process p $\in$ $\mathcal{P}$
    - $X^S_{r}$ - network binary for inventory of resource r  $\mathcal{R}^{storage}$ 



    $\textbf{Parametric Variables}$


    - $\alpha_{p}$ - uncertainty in production capacity of process p $\in$ $\mathcal{P}^{uncertain}$
    - $\beta_{r}$ - uncertainty in demand for resource r $\in$ $\mathcal{R}^{demand}$
    - $\gamma_{r}$ - uncertainty in purchase price for resource r $\in$ $\mathcal{R}^{cons}$
    - $\delta_{r}$ - uncertainty in consumption availability for resource r $\in$ $\mathcal{R}^{cons}$


    $\textbf{Parameters}$


    - $Cap^{P-max}_p$ - maximum production capacity of process p $\in$ $\mathcal{P}$
    - $Cap^{S-max}_r$ - maximum inventory capacity for process r $\in$ $\mathcal{R}^{storage}$
    - $Capex_p$ - capital expenditure for process p $\in$ $\mathcal{P}$ in time t $\in$ $\mathcal{T}$
    - $Price_{r,t}$ - purchase price for resource r $\in$ $\mathcal{R}^{cons}$ in time t $\in$ $\mathcal{T}$
    - $C^{max}_{r,t}$ - maximum consumption availability for resource r $\in$ $\mathcal{R}^{cons}$ in time t $\in$ $\mathcal{T}$
    - $D_{r,t}$ - demand for resource r $in$ $\mathcal{R}^{sell}$ in time t $\in$ $\mathcal{T}$

**MILP Formulation**

Given is a general MILP modeling and optimization framework for simultaneous network design and scheduling.

.. math::

    
    \begin{equation}
        min \hspace{1cm} \sum_{p \in \mathcal{P}} Capex_p \times Cap^P_p + \sum_{t \in \mathcal{T}} \sum_{r \in \mathcal{R}^{cons}} C_{r,t} \times Price_{r,t}
    \end{equation}


    \begin{equation}
        Cap^S_r \leq Cap^{S-max}_r \times X^S_r \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}
    \end{equation}

    \begin{equation}
        Cap^P_p \leq Cap^{P-max}_p \times X^P_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}
    \end{equation} 

    \begin{equation}
        P_{p,t} \leq Cap^{P}_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}
    \end{equation} 

    \begin{equation}
        Inv_{r,t} \leq Cap^{S}_r  \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}
    \end{equation} 


    \begin{equation}
        - S_{r,t} \leq - D_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}
    \end{equation}

    \begin{equation}
        C_{r,t} \leq C^{max}_{r,t} \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}
    \end{equation}


    \begin{equation}
        - S_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}, t \in \mathcal{T}
    \end{equation}

    \begin{equation}
        -Inv_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}, t \in \mathcal{T}
    \end{equation}

    \begin{equation}
        \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) + C_{r,t} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}, t \in \mathcal{T}
    \end{equation}

    \begin{equation}
        S_{r,t}, C_{r,t}, Inv_{r,t}, P_{p,t}, Cap^P_p, Cap^S_r \in R_{\geq 0}
    \end{equation}


**mpLP**

Reformulated, a general mpLP for the above MILP will looks something like this:

.. math::

        
    \begin{equation}
        min \hspace{1cm} \sum_{p \in \mathcal{P}} Capex_p \times P_p + \sum_{r \in \mathcal{R}^{cons}} C_r \times \gamma_r 
    \end{equation}


    \begin{equation}
        Inv_r \leq Cap^{S-max}_r \hspace{1cm} \forall r \in \mathcal{R}^{stored}
    \end{equation}

    \begin{equation}
        - S_r \leq - D_r \times \beta_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
    \end{equation}

    \begin{equation}
        C_r \leq C^{max}_r \times \delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons} 
    \end{equation}

    \begin{equation}
        P_p \leq Cap^{P-max}_p \times \alpha_p \hspace{1cm} \forall p \in \mathcal{P}
    \end{equation} 

    \begin{equation}
        - S_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}
    \end{equation}

    \begin{equation}
        -Inv_{r} + \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}
    \end{equation}

    \begin{equation}
        \sum_{p \in \mathcal{P}} P_{p} \times \eta(p,r) + C_{r} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

    \begin{equation}
        \alpha_p \in A_p \hspace{1cm} \forall p \in \mathcal{P}
    \end{equation}

    \begin{equation}
        \beta_r \in B_r \hspace{1cm} \forall r \in \mathcal{R}^{demand}
    \end{equation}

    \begin{equation}
        \gamma_r \in \Gamma_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

    \begin{equation}
        \delta_r \in \Delta_r \hspace{1cm} \forall r \in \mathcal{R}^{cons}
    \end{equation}

    \begin{equation}
        S_r, C_r, Inv_r, P_p \in R_{\geq 0}
    \end{equation}


**Example problem**

Let us now look at an example problem


.. math::
        
    \begin{equation}
        p \in \{LI_c, LI_d, WF, PV\} 
    \end{equation}


    \begin{equation}
        r \in \{charge, power, wind, solar\} 
    \end{equation}

    \begin{equation}
        min \hspace{1cm} \left[\begin{matrix}1302\\0\\990\\567\end{matrix}\right]^T \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right]
    \end{equation}


    \begin{equation}
        I_3\left[\begin{matrix}Inv_{charge}\\C_{wind}\\C_{solar}\\P_{LI_c}\\P_{LI_d}\end{matrix}\right] \leq \left[\begin{matrix} 100\\100\\100\\100\\100\end{matrix}\right]
    \end{equation}


    \begin{equation}
        I_3\left[\begin{matrix}-S_{power}\\P_{WF}\\P_{PV}\end{matrix}\right] \leq \left[\begin{matrix}-300 & 0 & 0\\0 & 100 & 0\\0 & 0 & 100\end{matrix}\right] \left[\begin{matrix}\beta_{power}\\ \alpha_{WF}\\\alpha_{PV}\end{matrix}\right]
    \end{equation}


    \begin{equation}
        I_4\left[\begin{matrix} - Inv_{charge} \\ -S_{power} \\ C_{wind} \\ C_{solar} \end{matrix}\right] + \left[\begin{matrix}0.89 & -1 & 0 & 0\\-1 & 1 & 0.85 & 0.75\\0 & 0 & -1 & 0\\0 & 0 & 0 & -1\end{matrix}\right] \left[\begin{matrix}P_{LI_c}\\P_{LI_d}\\P_{WF}\\P_{PV}\end{matrix}\right] = 0
    \end{equation}

    \begin{equation}
        \alpha_p \in \mathcal{A}_p \hspace{1cm} \forall p \in \{WF, PV\} 
    \end{equation}


    \begin{equation}
        \beta_r \in \mathcal{B}_r \hspace{1cm} \forall r \in \{Power\} 
    \end{equation}

Now we are ready to implement the above problem in energiapy

**Import modules**

.. code-block::

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

.. code-block::

    scales = Temporal_scale(discretization_list=[1])

**Declare the problem scenario**

.. code-block::

    Solar = Resource(name='Solar', cons_max=100, basis='MW', label='Solar Power')

    Wind = Resource(name='Wind', cons_max= 100, basis='MW', label='Wind Power')

    Power = Resource(name='Power', basis='MW', demand = True, label='Power generated', varying= VaryingResource.uncertain_demand)

    LiI = Process(name='LiI', storage= Power, capex = 1302, fopex= 0, vopex = 0,  prod_max=50, storage_loss = 0.11,  label='Lithium-ion battery', basis = 'MW')

    WF = Process(name='WF', conversion={Wind: -1, Power: 0.85},capex=990, fopex= 0, vopex=0, prod_max=100, label='Wind mill array', basis = 'MW', varying =  VaryingProcess.uncertain_capacity)

    PV = Process(name='PV', conversion={Solar: -1, Power: 0.75}, capex=567, fopex=0, vopex=0, prod_max=100, label = 'Solar PV', basis = 'MW', varying = VaryingProcess.uncertain_capacity)
    
    region = Location(name='region', processes= {LiI, PV, WF}, scales=scales, label='some region')
    
    example = Scenario(name= 'example', demand = {region: {Power: 100}}, network= region, scales= scales, label= 'example scenario')


**Generate the problem in matrix form**

.. code-block::

    A, b, c, H, CRa, CRb, F  = example.matrix_form()


**Solve the problem using the ppopt solver**

.. code-block::

    prog = MPLP_Program(A, b, c, H, CRa, CRb, F, equality_indices=[0,1,2,3])
    prog.solver.solvers['lp'] = 'gurobi'
    prog.warnings()
    prog.display_warnings()
    solution1 = solve_mpqp(prog, mpqp_algorithm.combinatorial)
