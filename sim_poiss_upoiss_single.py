from gc import collect as garbage_collect
from typing import Iterator, Optional, Tuple

import numpy as np
from typer import run as cli_run

from lib.psd import get_poiss_upoiss_psd


def make_signal_generator(
    desired_T: float,
    capture_rate: float,
    min_detachment_rate: float,
    max_detachment_rate: float,
    rng: np.random._generator.Generator,
) -> Iterator[Tuple[float, float]]:
    """Create generator object to generate gap and pulse durations."""
    experiment_T: float = 0

    while experiment_T < desired_T:
        # each capture center has random detachment rate
        detachment_rate = rng.uniform(low=min_detachment_rate, high=max_detachment_rate)
        current_gap = rng.exponential(scale=1 / detachment_rate)
        current_pulse = rng.exponential(scale=1 / capture_rate)

        # truncate experiment if it would run longer than desired duration
        if experiment_T + current_gap > desired_T:
            current_gap = desired_T - experiment_T
            current_pulse = 0
        experiment_T = experiment_T + current_gap
        if experiment_T + current_pulse > desired_T:
            current_pulse = desired_T - experiment_T
        experiment_T = experiment_T + current_pulse

        yield current_gap, current_pulse


def get_simulated_psd(
    imag_angular_freqs: np.ndarray,
    duration: float,
    pulse_magnitude: float,
    signal_generator: Iterator[Tuple[float, float]],
) -> Tuple[np.ndarray, int]:
    """Run single simulation, obtain PSD of a signal."""

    def __get_rect_fourier(
        imag_angular_freqs: np.ndarray,
        duration: float,
        start: float,
    ) -> np.ndarray:
        """Return Fourier transform of a rectangular pulse."""
        constant_terms = 1 / imag_angular_freqs
        profile = np.exp(imag_angular_freqs * duration) - 1
        variable_term = np.exp(imag_angular_freqs * start)
        return constant_terms * variable_term * profile

    gap_fourier = np.zeros(imag_angular_freqs.shape, dtype="complex128")
    pulse_fourier = np.zeros(imag_angular_freqs.shape, dtype="complex128")
    total_gap: float = 0
    total_pulse: float = 0
    n_pulses: int = 0
    for pulse, gap in signal_generator:
        gap_fourier += __get_rect_fourier(
            imag_angular_freqs,
            duration=gap,
            start=total_pulse + total_gap,
        )
        total_gap += gap

        pulse_fourier += __get_rect_fourier(
            imag_angular_freqs,
            duration=pulse,
            start=total_pulse + total_gap,
        )
        total_pulse += pulse
        if pulse > 0:
            n_pulses += 1

    mean_magnitude = pulse_magnitude * total_pulse / duration
    adjusted_pulse_magnitude = pulse_magnitude - mean_magnitude
    adjusted_gap_magnitude = -mean_magnitude

    gap_fourier = adjusted_gap_magnitude * gap_fourier
    pulse_fourier = adjusted_pulse_magnitude * pulse_fourier
    fourier = gap_fourier + pulse_fourier

    normalization = 2 / duration
    return normalization * (np.real(fourier) ** 2 + np.imag(fourier) ** 2), n_pulses


def main(
    repeats: int = 1,
    duration: float = 1e6,
    pulse_magnitude: float = 1,
    capture_rate: float = 1,
    min_detachment_rate: float = 0,
    max_detachment_rate: float = 1e3,
    min_freq: float = -1,
    max_freq: float = -1,
    n_freq: int = 100,
    archive_dir: str = "data",
    save_n_pulses: bool = False,
    seed: Optional[int] = None,
) -> None:
    """Simulate SNORPs with Poissonian pulses (fixed rate) and gaps (uniform rate).

    Input:
        repeats: (default: 1)
            Number of times to generate SNORP. Resulting PSD
            will be averaged over all runs.
        duration: (default: 1e6)
            Duration over which to simulate.
        pulse_magnitude: (default: 1)
            Fixed magnitude of the pulses in the signal.
        capture_rate: (default: 1)
            Rate at which charge carriers are captured.
        min_detachment_rate: (default: 0)
            Minimum expected detachment rate from the capturing potential.
        max_detachment_rate: (default: 1e3)
            Maximum expected detachment rate from the capturing potential
        min_freq: (default: -1)
            Minimum frequency to observe. If negative value is
            passed (which is the default), then the minimum
            frequency is calculated automatically based on
            simulation parameters.
        max_freq: (default: -1)
            Maximum frequency to observe. If negative value is
            passed (which is the default), then the maximum
            frequency is calculated automatically based on
            simulation parameters.
        n_freq: (default: 100)
            Number of frequencies to consider within the given
            (or automatically selected) range. Includes end
            points.
        archive_dir: (default: "data")
            Folder in which to save output files.
        save_n_pulses: (default: False)
            Should the number of pulses generated during each realization
            be saved to a file?
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
    model_info = f"poiss{capture_rate*10000:.0f}.upoiss{min_detachment_rate*10000:.0f}_{max_detachment_rate:.0f}"
    simulation_filename = f"{model_info}.seed{seed:d}"
    psd_path = f"{archive_dir}/{simulation_filename}.psd.csv"
    n_pulses_path = f"{archive_dir}/{simulation_filename}.n_pulses.csv"

    # set frequency range
    if max_freq < 0:
        max_freq = 10 * max_detachment_rate / (np.pi**2)
    if min_freq < 0:
        min_freq = np.max(
            [
                1 / duration,
                0.1 * min_detachment_rate / (2 * np.pi),
            ]
        )
    freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), n_freq)
    freqs = np.unique(np.round(duration * freqs)) / duration  # round to natural freqs
    freqs = freqs[freqs > 0]  # remove zero frequency
    n_freq = len(freqs)

    imag_angular_freqs = -2j * np.pi * freqs

    # main simulation loop
    sim_psds = np.zeros((repeats, n_freq))
    n_pulses = np.zeros((repeats))
    for sim_idx in range(repeats):
        signal_generator = make_signal_generator(
            duration,
            capture_rate,
            min_detachment_rate,
            max_detachment_rate,
            rng,
        )
        sim_psds[sim_idx, :], n_pulses[sim_idx] = get_simulated_psd(
            imag_angular_freqs, duration, pulse_magnitude, signal_generator
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
        n_carriers=1,
    )

    np.savetxt(
        psd_path,
        np.log10(np.vstack((freqs, sim_psd, theory_psd)).T),
        delimiter=",",
        fmt="%.4f",
    )

    if save_n_pulses:
        np.savetxt(
            n_pulses_path,
            n_pulses,
            delimiter=",",
            fmt="%.0f",
        )


if __name__ == "__main__":
    cli_run(main)
