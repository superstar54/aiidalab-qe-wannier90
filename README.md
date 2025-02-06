# aiidalab-qe-wannier90







## Compile Wanntier90

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
