# aiidalab-qe-wannier90

A plugin for running Wannier calculations inside the AiiDAlab Quantum ESPRESSO App.

## Features

- **Band structure comparison** with DFT bands.
- With predefined protocols (`fast`, `balanced`, `stringent`)
- **Optional real-space Wannier functions** (3D visualization) with the atomic structure.

<img src="docs/source/_static/images/overview.png"  width="800px"/>


<!-- <img src="docs/source/_static/images/qeapp-wannier90-wf.gif"  width="100%"/> -->


## Usage
Run Wannier calculations via the AiiDAlab QE App GUI.


## Compile Wanntier90

This plugin requires the Wannier90 code from the latest source code from the [Wannier90 GitHub repository](https://github.com/wannier-developers/wannier90).

To compile Wannier90, follow the instructions below:

```bash
git clone https://github.com/wannier-developers/wannier90.git
cd wannier90
sudo apt update
sudo apt install gfortran libblas-dev liblapack-dev
cp config/make.inc.gfort make.inc
make wannier
```


validate the installation by running the following command:

```bash
./wannier90.x -h
```



## Isosurface

I used PythonJob to calculate the isosurface of the wannier function, and save the mesh data as AiiDA output node, then visualize the isosurface using the `weas-widget`. This avoids the need to download and save the large density file.


### Set up PythonJob code
To setup the `python` code for isosurface calculation, you need to install the following packages in the Python environment:

```
cloudpickle
scikit-image
ase
```

Then one can use `verdi` command create the `pythonjob` code. Here is an example configuration file to setup the `pythonjob` code:

```yaml
---
label: python3
description: python3.9.10 at Merlin 7
default_calc_job_plugin: pythonjob.pythonjob
filepath_executable: /opt/psi/Programming/Python/3.9.10/bin/python
prepend_text: |
    module purge
    module load Python/3.9.10
append_text: ''
```
Run the fowlling command to create the `pythonjob` code in your AiiDA profile:

```
verdi code create core.code.installed --config pythonjob-code.yaml
```
