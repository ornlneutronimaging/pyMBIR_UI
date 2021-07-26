# pyMBIR_UI

UI for pyMBIR software. 

## Installation

Please install the pyMBIR code from the git repo before installing the UI t prevent package conflicts. 

### Git
clone the source file from github

> git clone https://github.com/ornlneutronimaging/pyMBIR_UI.git

### Create conda environment

> conda create -n pymbir_ui python=3.7

> source activate pymbir_ui

### Install required packages:

> conda install -c anaconda qtpy

> conda install -c conda-forge tomopy

> pip install NeuNorm

> conda install -c anaconda pyqtgraph=0.11.0

### install 

> cd pymbir_ui

> pip install -e .

### run UI

> python -m pyMBIR_UI
