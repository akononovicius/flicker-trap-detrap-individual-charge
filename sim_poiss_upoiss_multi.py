from gc import collect as garbage_collect
from typing import Optional

import numpy as np
from typer import run as cli_run

from lib.psd import get_poiss_upoiss_psd, get_psd_at_freqs


def __generate_initial_state(
    desired_T: float,
    n_carriers: int,
    capture_rate: float,
    min_detachment_rate: float,
    max_detachment_rate: float,
    rng: np.random._generator.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate statistically correct initial state."""

    def __mean_free_carriers(
        n_carriers: int,
        desired_T: float,
        capture_rate: float,
        min_detachment_rate: float,
        max_detachment_rate: float,
    ) -> float:
        """Calculate mean number of free carriers."""
        mean_free_time = 1 / capture_rate

        min_detachment_rate = np.max([min_detachment_rate, 1 / desired_T])
        mean_captured_time = np.log(max_detachment_rate / min_detachment_rate) / (
            max_detachment_rate - min_detachment_rate
        )

        return n_carriers * mean_free_time / (mean_free_time + mean_captured_time)

    def __sample_escape_wait_times(
        min_detachment_rate: float,
        max_detachment_rate: float,
        rng: np.random._generator.Generator,
        size: int = 1,
    ) -> np.ndarray | float:
        """Generate time until escape, if observation starts not at capture."""
        cdf = rng.uniform(size=size)
        detachment_rate = min_detachment_rate * (
            (max_detachment_rate / min_detachment_rate) ** cdf
        )
        return rng.exponential(scale=1 / detachment_rate)

    carrier_state = np.zeros(n_carriers, dtype=int)
    mfc = __mean_free_carriers(
        n_carriers,
        desired_T,
        capture_rate,
        min_detachment_rate,
        max_detachment_rate,
    )
    free_carriers = (int)(np.floor(mfc))
    if rng.uniform() < (mfc - free_carriers):
        free_carriers = free_carriers + 1

    carrier_state[:free_carriers] = 1

    switch_time = np.zeros(n_carriers)
    switch_time[:free_carriers] = rng.exponential(
        scale=1 / capture_rate, size=free_carriers
    )
    if n_carriers > free_carriers:
        switch_time[free_carriers:] = __sample_escape_wait_times(
            np.max([min_detachment_rate, 1 / desired_T]),
            max_detachment_rate,
            rng,
            size=n_carriers - free_carriers,
        )

    return carrier_state, switch_time


def generate_signal(
    n_samples: int,
    sample_period: float,
    n_carriers: int,
    capture_rate: float,
    min_detachment_rate: float,
    max_detachment_rate: float,
    rng: np.random._generator.Generator,
) -> tuple[np.ndarray, float]:
    """Generate a multiple carrier signal as per the condensed matter model."""
    desired_T = n_samples * sample_period
    signal = np.zeros(n_samples, dtype=float)

    carrier_state, switch_time = __generate_initial_state(
        desired_T,
        n_carriers,
        capture_rate,
        min_detachment_rate,
        max_detachment_rate,
        rng,
    )
    free_carriers = np.sum(carrier_state)

    signal[0] = free_carriers
    mean_signal = signal[0]
    for sample_idx in range(1, n_samples):
        next_T = sample_idx * sample_period
        switch_carriers = np.where(switch_time < next_T)[0]
        while len(switch_carriers) > 0:
            for carrier_idx in switch_carriers:
                if carrier_state[carrier_idx] == 0:
                    free_carriers = free_carriers + 1
                    carrier_state[carrier_idx] = 1
                    switch_time[carrier_idx] += rng.exponential(scale=1 / capture_rate)
                else:
                    free_carriers = free_carriers - 1
                    carrier_state[carrier_idx] = 0
                    detachment_rate = rng.uniform(
                        low=min_detachment_rate, high=max_detachment_rate
                    )
                    switch_time[carrier_idx] += rng.exponential(
                        scale=1 / detachment_rate
                    )
            switch_carriers = np.where(switch_time < next_T)[0]
        signal[sample_idx] = free_carriers
        mean_signal = mean_signal + (signal[sample_idx] - mean_signal) / (
            sample_idx + 1
        )

    return signal, mean_signal


def main(
    repeats: int = 1,
    n_carriers: int = 1,
    n_samples: int = 2**20,
    sample_period: float = 1e-3,
    pulse_magnitude: float = 1,
    capture_rate: float = 1,
    min_detachment_rate: float = 0,
    max_detachment_rate: float = 1e3,
    n_freq: int = 100,
    archive_dir: str = "data",
    signal_output: bool = False,
    seed: Optional[int] = None,
):
    """Simulate SNORPs with Poissonian pulses (fixed rate) and gaps (uniform rate).

    Input:
        repeats: (default: 1)
            Number of times to generate SNORP. Resulting PSD
            will be averaged over all runs.
        n_carriers: (default: 1)
            Number of independent charge carriers.
        n_samples: (default: 2**20)
            Number of temporal samples to take.
        sampling_period: (default: 1e-3)
            Sampling period for temporal sampling.
        pulse_magnitude: (default: 1)
            Fixed magnitude of the pulses in the signal.
        capture_rate: (default: 1)
            Rate at which charge carriers are captured.
        min_detachment_rate: (default: 0)
            Minimum expected detachment rate from the capturing potential.
        max_detachment_rate: (default: 1e3)
            Maximum expected detachment rate from the capturing potential
        n_freq: (default: 100)
            Number of frequencies to take from the available interval.
        archive_dir: (default: "data")
            Folder in which to save output files.
        signal_output: (default: False)
            Should the signal be output?
        seed: (default: None)
            RNG seed. If no value is passed, then it will be randomly
            generated by `np.random.randint(0, int(2**20))`

    Output:
        Function returns nothing, but saves one file, which
        contains the numerically calculated PSD and its
        theoretical estimate.
    """
    # auto-generate seed
    if seed is None:
        np.random.seed()
        seed = np.random.randint(0, int(2**20))

    if min_detachment_rate > max_detachment_rate:
        max_detachment_rate = min_detachment_rate

    # RNG setup
    rng = np.random.default_rng(seed)

    # simulation archival setup
    model_info = f"poiss{capture_rate*10000:.0f}.upoiss{min_detachment_rate*10000:.0f}_{max_detachment_rate:.0f}.nc{n_carriers:.0f}.multi"
    simulation_filename = f"{model_info}.seed{seed:d}"
    psd_path = f"{archive_dir}/{simulation_filename}.psd.csv"
    signal_path = f"{archive_dir}/{simulation_filename}.{'{:d}'}.series.csv"

    # main simulation loop
    duration = n_samples * sample_period
    natural_freqs = np.unique(
        np.floor(np.logspace(0, np.log10(n_samples // 2), num=n_freq)).astype(int)
    )
    freqs = natural_freqs / duration
    n_freq = len(freqs)
    sim_psds = np.zeros((repeats, n_freq))
    for sim_idx in range(repeats):
        signal, mean_signal = generate_signal(
            n_samples,
            sample_period,
            n_carriers,
            capture_rate,
            min_detachment_rate,
            max_detachment_rate,
            rng,
        )
        if signal_output:
            np.savetxt(
                signal_path.format(sim_idx),
                signal,
                delimiter=",",
                fmt="%.0f",
            )
        sim_psds[sim_idx, :] = get_psd_at_freqs(
            signal - mean_signal,
            natural_freqs,
            sample_freq=1 / sample_period,
        )
        garbage_collect()

    # numerical PSD
    sim_psd = np.mean(sim_psds, axis=0)

    # theoretical PSD
    theory_psd = get_poiss_upoiss_psd(
        freqs,
        pulse_magnitude,
        capture_rate,
        np.max([min_detachment_rate, 1 / duration]),
        max_detachment_rate,
        n_carriers=n_carriers,
    )

    np.savetxt(
        psd_path,
        np.log10(np.vstack((freqs, sim_psd, theory_psd)).T),
        delimiter=",",
        fmt="%.4f",
    )


if __name__ == "__main__":
    cli_run(main)
