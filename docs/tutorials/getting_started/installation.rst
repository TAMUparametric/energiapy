.. _installation:

Installation
============

This tutorial should help you get Energia up and running on your PC.

What you are going to need:

1. A computer
2. Python >=3.12
3. Will power


Folder Structure
----------------

An example structure of your project folder could look like this:


.. code-block:: text

    ├── projects/
    │   ├── .venv/
    │   ├── lifecycle.py
    │   └── technoeconomic.ipynb
    ├── data/
    │   ├── weather.csv
    │   └── cost.xlsx
    └── results/
        └── base_case/
            ├── run.enrg
            ├── emission.csv
            └── cost_breakdown.png

The **projects/** folder contains your scripts and notebooks. 
A virtual environment (**.venv/**) can be placed here. This will contain all the scripts necessary to run Energia and its dependencies.
**lifecycle.py** and **technoeconomic.ipynb** are example scripts written in Python script and Jupyter Notebook, respectively.
Your code in Energia will be written in these. It is good practice to have dedicated folders for your input **data** and output **results**.



Setting up an Environment
-------------------------

This tutorial focuses on creating virtual environments. Conda environments can also be used.
Inside your terminal (Command Prompt, PowerShell, bash, etc.), navigate to your project folder.
Run the following command.

.. code-block:: bash

    python3.13 -m venv .venv

.. tip:: For a conda environment:

    .. code-block:: bash

        conda create --name env python=3.13

Now that your environment is ready, you will need to activate it.


Activating an Environment
-------------------------

Make sure that your environment is activated before installing Energia or running any scripts.
It will show up in your terminal prompt, e.g. **(.venv) path/to//projects>**.

.. code-block:: bat

    .venv\Scripts\activate

.. tip:: On Mac or Linux:

    .. code-block:: bash

        source .venv/bin/activate

.. tip:: For a conda environment:

    .. code-block:: bash

        conda activate env


Installing Energia
------------------

Energia supports the standard pip installation. 
This will populate your activated environment with Energia and its dependencies.

.. code-block:: bash

    pip install energiapy


Once installed, you may need to restart your environment (or terminal). 


.. _ides:

Integrated Development Environments (IDEs)
------------------------------------------

Creating environments, managing projects, and such can be simpler on IDEs. Here are some guides for configuring popular IDEs:

- **Visual Studio Code**: `Python environments in VS Code <https://code.visualstudio.com/docs/python/environments>`_

- **PyCharm**: `Configuring Python interpreter <https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html>`_

- **Google Colab**: `Using a local runtime <https://colab.research.google.com/notebooks/snippets/importing_libraries.ipynb>`_


