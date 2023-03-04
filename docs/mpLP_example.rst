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
