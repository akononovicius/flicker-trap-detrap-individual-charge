#!/usr/bin/env bash

# results used in sample-psd figure
python sim_poiss_upoiss_single.py --repeats 100 --duration 1e6 --min-detachment-rate 1e-4 --max-detachment-rate 1e4 --min-freq 1e-6 --max-freq 1e5 --seed 6288

# results used in different-duration figure
python sim_poiss_upoiss_single.py --duration 1e4 --min-detachment-rate 0 --max-detachment-rate 1e3 --min-freq 1e-4 --max-freq 1e4 --seed 18557
python sim_poiss_upoiss_single.py --duration 1e6 --min-detachment-rate 0 --max-detachment-rate 1e3 --min-freq 1e-6 --max-freq 1e4 --seed 16022
python sim_poiss_upoiss_single.py --repeats 1000 --duration 1e6 --min-detachment-rate 0 --max-detachment-rate 1e3 --min-freq 1e-6 --max-freq 1e4 --seed 23245
python sim_poiss_upoiss_single.py --duration 1e8 --min-detachment-rate 0 --max-detachment-rate 1e3 --min-freq 1e-8 --max-freq 1e4 --seed 11921

# results used in multicarrier figure
python sim_poiss_upoiss_multi.py --n-carriers 1000 --n-samples 134217728 --sample-period 5e-5 --min-detachment-rate 0 --max-detachment-rate 1e3 --signal-output --seed 23567
# previous command generates large file with 134217728 signal values, gzip it!
if [ -n $( command -v "gzip" ) ]; then
    gzip -f "data/poiss10000.upoiss0_1000.nc1000.multi.seed23567.0.series.csv"
fi
