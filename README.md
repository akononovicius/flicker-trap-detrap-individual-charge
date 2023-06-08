# 1/f noise from the trapping-detrapping process of individual charge carriers

Typically it is assumed that trapping and detrapping in semiconductor
materials are Poisson processes. When both processes are indeed Poisson then
the signal will have Lorentzian power spectral density. Most well-known
models (like McWhorter or van der Ziel models) assume that the superposition
of Lorentzian power spectral densities is necessary to obtain 1/f noise.
While that assumption is correct, it is not the only way to obtain 1/f noise
in a model of semiconductor material [1].

In we have studied a trapping-detrapping process assuming that detrapping
rates are heterogeneous. Namely, detrapping rates were assumed to be
randomly sampled from the uniform distribution. This allows to obtain 1/f
noise even when a single charge carrier generates the signal.

This repository contains the code used to perform the simulations reported
in [1]. Simulations can be run by running `sim.sh` script. Figures can be
reproduced by running `fig.sh` script.

## On the difference between the two `sim_*.py` files

Two different simulation scripts are used. This section briefly discussed
the main differences between them.

`sim_poiss_upoiss_single.py` script performs simulations assuming that the
signal is created by a single charge carrier. It uses specifically tailored
algorithm to calculate power spectral densities. This simulation script is
designed in the same way as the duration based simulation scripts from
[flicker-snorp](https://github.com/akononovicius/flicker-snorp) repository
(which is based on an earlier article [2]).

`sim_poiss_upoiss_multi.py` allows user to specify the number of charge
carriers to use in simulations. The user could choose to simulate a single
charge carrier, and obtain results similar to the ones that would be
obtained using `sim_poiss_upoiss_single.py`. Though the results won't be
identical even for the same seed, because scripts are designed differently,
and they require slightly different input arguments. Drawback of using
`sim_poiss_upoiss_multi.py` is that it first generates signal, taking fixed
number of samples using predefined sampling period, and then stores it in
memory (it is a big memory hog!). Only afterwards it uses a generic
`scipy.signal.periodogram` function to calculate power spectral density.

## References

1. A. Kononovicius, B. Kaulakys. *1/f noise from the trapping-detrapping
   process of individual charge carriers.* (under review)
2. A. Kononovicius, B. Kaulakys. *1/f noise from the sequence of
   nonoverlapping rectangular pulses.* Physical Review E **107**: 034117
   (2023). [doi:
   10.1103/PhysRevE.107.034117](https://doi.org/10.1103/PhysRevE.107.034117).
   [arXiv:2210.11792
   [cond-mat.stat-mech]](https://arxiv.org/abs/2210.11792).
