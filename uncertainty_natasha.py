
#%%
# flexibility test: given a fixed range for the uncertain parameter Fh,  where is the critical point?

# case study source: https://doi.org/10.1016/0098-1354(87)87011-4 (Grossmann and Floudas 1987)

__author__ = "Natasha Jane Chrisandina, Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Natasha Jane Chrisandina", "Rahul Kakodkar", "Efstratios N. Pistikopoulos", "Mahmoud M. El-Halwagi"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Natasha Jane Chrisandina"
__email__ = "nchrisandina@tamu.edu"
__status__ = "Production"

from sys import executable
from pyomo.environ import *
from pyomo.core import *
import numpy as np

model = ConcreteModel()



#================================================================================================================
    #*                                                 Sets 
#================================================================================================================
    
J = np.array([0,1,2,3])
model.ineq = Set(initialize = J, doc = 'inequalities indices')

#================================================================================================================
    #*                                                 Parameters 
#================================================================================================================
 
bigM = 1000


#================================================================================================================
    #*                                                 Variables 
#================================================================================================================
 

model.u = Var(doc = 'objective function variable')
model.Fh = Var(bounds = (1,1.4), initialize = 1.4, doc = 'uncertain parameter')
model.Qc = Var(domain = NonNegativeReals, doc = 'control variable')
model.lamb = Var(model.ineq, domain = NonNegativeReals, doc = 'KKT multiplier')
model.s = Var(model.ineq, domain = NonNegativeReals, doc = 'slack')
model.y = Var(model.ineq, domain = Binary, doc = '1 if constraint j is active')


#================================================================================================================
    #*                                                 Constraints 
#================================================================================================================
 
model.constraint1 = ConstraintList()
model.constraint1.add(-25 + model.Qc*((1/model.Fh) - 0.5) + (10/model.Fh) + model.s[0] == model.u)
model.constraint1.add(-190 + (10/model.Fh) + (model.Qc/model.Fh) + model.s[1] == model.u)
model.constraint1.add(-270 + (model.Qc/model.Fh) + (250/model.Fh) + model.s[2] == model.u)
model.constraint1.add(260 - (model.Qc/model.Fh) - (250/model.Fh) + model.s[3] == model.u)

model.constraint2 = Constraint(expr = sum(model.lamb[j] for j in model.ineq) == 1)

model.constraint3 = Constraint(expr = model.lamb[0]*((1/model.Fh) - 0.5) + (model.lamb[1]/model.Fh) + (model.lamb[2]/model.Fh) - (model.lamb[3]/model.Fh) == 0)

model.constraint4 = ConstraintList()
for j in model.ineq:
    model.constraint4.add(model.s[j] - bigM*(1-model.y[j]) <= 0)
    model.constraint4.add(model.lamb[j] - model.y[j] <= 0)

model.constraint5 = Constraint(expr = sum(model.y[j] for j in model.ineq) == 2)

model.obj = Objective(expr = model.u, sense = maximize)

result = SolverFactory('gams').solve(model, tee=True)

print('The value of the control variable is ', value(model.Qc))
print('The value of the uncertain parameter is ', value(model.Fh))
print('The value of u is ', value(model.u))
# %%

# flexibility index. Given no range for the uncertain parameter, how big a deviation can we have?

from sys import executable
from pyomo.environ import *
from pyomo.core import *
import numpy as np

model = ConcreteModel()


#================================================================================================================
    #*                                                 Sets 
#================================================================================================================
 
J = np.array([0,1,2,3])
model.ineq = Set(initialize = J)


#================================================================================================================
    #*                                                 Parameters 
#================================================================================================================
 
bigM = 1000
Fh_normal = 1.4


#================================================================================================================
    #*                                                 Variables 
#================================================================================================================
 
model.delta = Var(doc = 'flexibility index')
model.Fh = Var(initialize = Fh_normal, doc = 'uncertain parameter')
model.Qc = Var(domain = NonNegativeReals, doc = 'control variable')
model.lamb = Var(model.ineq, domain = NonNegativeReals, doc = 'KKT multiplier')
model.s = Var(model.ineq, domain = NonNegativeReals, doc = 'slack')
model.y = Var(model.ineq, domain = Binary, doc = '1 if constraint is active')


#================================================================================================================
    #*                                                 Constraints 
#================================================================================================================
 
model.constraint1 = ConstraintList()
model.constraint1.add(-25 + model.Qc*((1/model.Fh) - 0.5) + (10/model.Fh) + model.s[0] == 0)
model.constraint1.add(-190 + (10/model.Fh) + (model.Qc/model.Fh) + model.s[1] == 0)
model.constraint1.add(-270 + (model.Qc/model.Fh) + (250/model.Fh) + model.s[2] == 0)
model.constraint1.add(260 - (model.Qc/model.Fh) - (250/model.Fh) + model.s[3] == 0)

model.constraint2 = Constraint(expr = sum(model.lamb[j] for j in model.ineq) == 1)

model.constraint3 = Constraint(expr = model.lamb[0]*((1/model.Fh) - 0.5) + (model.lamb[1]/model.Fh) + (model.lamb[2]/model.Fh) - (model.lamb[3]/model.Fh) == 0)

model.constraint4 = ConstraintList()
for j in model.ineq:
    model.constraint4.add(model.s[j] - bigM*(1-model.y[j]) <= 0)
    model.constraint4.add(model.lamb[j] - model.y[j] <= 0)

model.constraint5 = Constraint(expr = sum(model.y[j] for j in model.ineq) == 2)

model.constraint6 = ConstraintList()
model.constraint6.add(model.Fh >= Fh_normal - model.delta)
model.constraint6.add(model.Fh <= Fh_normal + model.delta)

model.obj = Objective(expr = model.delta, sense = minimize)

result = SolverFactory('gams').solve(model, tee=True)

print('The value of the control variable is ', value(model.Qc))
print('The value of the uncertain parameter is ', value(model.Fh))
print('The value of delta is ', value(model.delta))
# %%

# example 4 in Grossmann and Floudas 1987 paper
from sys import executable
from pyomo.environ import *
from pyomo.core import *
import numpy as np

model = ConcreteModel()


#================================================================================================================
    #*                                                 Sets 
#================================================================================================================

J = np.array([0,1,2,3,4])
model.ineq = Set(initialize = J)

#================================================================================================================
    #*                                                 Parameters 
#================================================================================================================

#design
P1 = 100
bigM = 10000000
W = 31.2
H = 1.3
D = 0.0762
C_max = 0.039673
r = 0.05
eta = 20

#uncertain parameters
P2nominal = 800
P2plus = 200
P2minus = 500

mnominal = 10
mplus = 2
mminus = 5

nunominal = 0.5
nuplus = 0.05
numinus = 0.05

knominal = 9.101e-6
kplus = 0.45505e-6
kminus = 0.45505e-6

rhonominal = 1000
rhoplus = 50
rhominus = 50

#================================================================================================================
    #*                                                 Variables 
#================================================================================================================

#control
model.Cv = Var(bounds = (0.000001, 10000), doc ='control variable')

#uncertain parameters
model.P2 = Var(domain = NonNegativeReals, doc = 'uncertain pressure')
model.bigM = Var(domain = NonNegativeReals, doc = 'uncertain big M parameter') 
model.nu = Var(domain = NonNegativeReals, doc = 'uncertain parameter nu')
model.k = Var(domain = NonNegativeReals, doc = 'uncertain parameter k')
model.rho = Var(bounds = (0.1,10000), doc = 'uncertain density parameter')

# MIP formulation
model.delta = Var(domain = NonNegativeReals, doc = 'flexibility index')
model.lamb = Var(model.ineq, domain = NonNegativeReals, doc = 'KKT multiplier')
model.y = Var(model.ineq, domain = Binary, doc = '1 if constraint j is active')




#================================================================================================================
    #*                                                 Constraints 
#================================================================================================================

model.constraint1 = ConstraintList()
model.constraint1.add(P1 + model.rho*H - eta - ((model.bigM**2)/(model.rho * (model.Cv**2))) - (model.k * (model.bigM**1.84)/(D**5.16)) - model.P2 + model.s[0] == 0)
model.constraint1.add(-P1 - model.rho*H - eta + ((model.bigM**2)/(model.rho * (model.Cv**2))) + (model.k * (model.bigM**1.84)/(D**5.16)) + model.P2 + model.s[1] == 0)
model.constraint1.add(model.bigM*H - model.nu*W + model.s[2] == 0)
model.constraint1.add(model.Cv - C_max + model.s[3] == 0)
model.constraint1.add(-model.Cv + r*C_max + model.s[4] == 0)

model.constraint2 = Constraint(expr = sum(model.lamb[j] for j in model.ineq) == 1)

model.constraint3 = Constraint(expr = (model.lamb[0]*2*(model.bigM**2)/((model.Cv**3)*model.rho)) + (model.lamb[1]*-2*(model.bigM**2)/((model.Cv**3)*model.rho)) + (model.lamb[2]*0) + (model.lamb[3]*1) + (model.lamb[4]*-1) == 0)

model.constraint4 = ConstraintList()
for j in model.ineq:
    model.constraint4.add(model.s[j] - bigM*(1-model.y[j]) <= 0)
    model.constraint4.add(model.lamb[j] - model.y[j] <= 0)

model.constraint5 = Constraint(expr = sum(model.y[j] for j in model.ineq) == 2)

model.constraint6 = ConstraintList()
model.constraint6.add(model.P2 >= P2nominal - P2minus*model.delta)
model.constraint6.add(model.P2 <= P2nominal + P2plus*model.delta)
model.constraint6.add(model.bigM >= mnominal - mminus*model.delta)
model.constraint6.add(model.bigM <= mnominal + mplus*model.delta)
model.constraint6.add(model.nu >= nunominal - numinus*model.delta)
model.constraint6.add(model.nu <= nunominal + nuplus*model.delta)
model.constraint6.add(model.k >= knominal - kminus*model.delta)
model.constraint6.add(model.k <= knominal + kplus*model.delta)
model.constraint6.add(model.rho >= rhonominal - rhominus*model.delta)
model.constraint6.add(model.rho <= rhonominal + rhoplus*model.delta)


# model.constraint7 = ConstraintList()
# model.constraint7.add(model.y[1] == 1)
# model.constraint7.add(model.y[3] == 1)

model.obj = Objective(expr = model.delta, sense = minimize)

result = SolverFactory('gams', solver = 'BARON').solve(model, tee=True)


model.delta.pprint()
model.y.pprint()

# %%
