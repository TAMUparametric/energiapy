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



*Continuous Variables*


- P\ :sub:`p,t` - production level of p :math:`{\\in}`  P in time period t :math:`{\\in}` T  
    
- C\ :sub:`r,t` - consumption of r :math:`{\\in}` R\ :sup:`cons` time period t :math:`{\\in}` T 
    
- S\ :sub:`r,t` - discharge of r :math:`{\\in}` R\ :sup:`demand` time period t :math:`{\\in}` T 
    
- Inv\ :sub:`r,t` - inventory level of r :math:`{\\in}` R\ :sup:`storage`  in time period t :math:`{\\in}` T
    
- Cap\ :sup:`S` \ :sub:`r` - installed inventory capacity for resource r :math:`{\\in}`  R\ :sup:`storage` 
    
- Cap\ :sup:`P` \ :sub:`p` - installed production capacity for process p :math:`{\\in}` P
    



*Binary Variables*


- X\ :sup:`P` \ :sub:`p` - network binary for production process p :math:`{\\in}` P
- X\ :sup:`S` \ :sub:`r` - network binary for inventory of resource r :math:`{\\in}` R\ :sup:`storage`



*Parametric Variables*


- :math:`{\\alpha}` \ :sub:`p` - uncertainty in production capacity of process p :math:`{\\in}` P\ :sup:`uncertain`
- :math:`{\\beta}` \ :sub:`r` - uncertainty in demand for resource r :math:`{\\in}` R\ :sup:`demand`
- :math:`{\\gamma}` \ :sub:`r` - uncertainty in purchase price for resource r :math:`{\\in}` R\ :sup:`cons`
- :math:`{\\delta}` \ :sub:`r` - uncertainty in consumption availability for resource r :math:`{\\in}` R\ :sup:`demand`


*Parameters*


- Cap\ :sup:`P-max` \ :sub:`p` - maximum production capacity of process p :math:`{\\in}` P
- Cap\ :sup:`S-max` \ :sub:`r` - maximum inventory capacity for process r :math:`{\\in}` R\ :sup:`storage`
- Capex\ :sub:`p` - capital expenditure for process p :math:`{\\in}` P in time t :math:`{\\in}` T
- Price\ :sub:`r,t ` - purchase price for resource r :math:`{\\in}` R\ :sup:`cons` in time t :math:`{\\in}` T
- C\ :sup:`max ` \ :sub:`r,t` - maximum consumption availability for resource r :math:`{\\in}` R\ :sup:`cons` in time t :math:`{\\in}` T}
- D\ :sub:`r,t` - demand for resource r in R\ :sup:`sell` in time t :math:`{\\in}` T

**MILP Formulation**

Given is a general MILP modeling and optimization framework for simultaneous network design and scheduling.


.. math::
    \begin{equation}
        min \hspace{1cm} \sum_{p \in \mathcal{P}} Capex_p \times Cap^P_p + \sum_{t \in \mathcal{T}} \sum_{r \in \mathcal{R}^{cons}} C_{r,t} \times Price_{r,t}
    \end{equation}

.. math::
    \begin{equation}
        Cap^S_r \leq Cap^{S-max}_r \times X^S_r \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}
    \end{equation}

.. math::
    \begin{equation}
        Cap^P_p \leq Cap^{P-max}_p \times X^P_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}
    \end{equation} 

.. math::
    \begin{equation}
        P_{p,t} \leq Cap^{P}_p  \hspace{1cm} \forall p \in \mathcal{P}, t \in \mathcal{T}
    \end{equation} 

.. math::
    \begin{equation}
        Inv_{r,t} \leq Cap^{S}_r  \hspace{1cm} \forall r \in \mathcal{R}^{storage}, t \in \mathcal{T}
    \end{equation} 

.. math::
    \begin{equation}
        - S_{r,t} \leq - D_{r,t}  \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}
    \end{equation}

.. math::
    \begin{equation}
        C_{r,t} \leq C^{max}_{r,t} \hspace{1cm} \forall r \in \mathcal{R}, t \in \mathcal{T}
    \end{equation}

.. math::
    \begin{equation}
        - S_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{sell}, t \in \mathcal{T}
    \end{equation}

.. math::
    \begin{equation}
        -Inv_{r,t} + \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) = 0 \hspace{1cm} \forall r \in \mathcal{R}^{stored}, t \in \mathcal{T}
    \end{equation}

.. math::
    \begin{equation}
        \sum_{p \in \mathcal{P}} P_{p,t} \times \eta(p,r) + C_{r,t} = 0 \hspace{1cm} \forall r \in \mathcal{R}^{cons}, t \in \mathcal{T}
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

