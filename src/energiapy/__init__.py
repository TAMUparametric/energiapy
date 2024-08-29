"""energiapy was developed as a PhD project by Rahul Kakodkar

The project was supervised by Prof. Efstratios (Stratos) N. Pistikopoulos

It is licensed under the MIT License

Attributes: 
    Bound - is a bound on some component Task 

    Exact - is an exact value of some component Task
        The subtypes are:
            Exp (expenses) - how much Cash is spent or earned 
            Emn (emissions) - amount of Emission released
            Use (use) - is the use of Land or Material
            Lss (losses) - is the loss of Resource
            Rte (rates) - rates such as speed, setup_time

    Balance - is the balance of Resource
        The subtypes are: 
            Conversion: for Process
            Inventory: for Storage
            Freight: for Transit

The naming convention is as follows:

    Variables: Task (if not Parent), TaskParent (if Parent)
    
    



"""
