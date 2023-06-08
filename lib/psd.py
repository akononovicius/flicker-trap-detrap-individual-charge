import numpy as np
from scipy.signal import periodogram  # type: ignore


def get_psd_at_freqs(
    signal: np.ndarray | list,
    which_freq_idx: np.ndarray | list,
    sample_freq: float = 1,
) -> np.ndarray:
    """Calculate PSD via scipy, and report at selected frequencies.

    Input:
        signal:
            Array of observed values of the signal.
        which_freq_idx:
            Which natural frequencies to report. 1/T is first natural
            frequency, 2/T is second, and so on. Integer values are
            expected.
        sample_freq: (default: 1)
            Frequency with which the signal was sampled.

    Output:
        PSD values (via scipy.signal.periodogram) at desired natural
        frequencies.
    """
    _, psd = periodogram(signal, fs=sample_freq)
    return psd[which_freq_idx]


def get_poiss_upoiss_psd(
    freqs: np.ndarray,
    pulse_magnitude: float,
    capture_rate: float,
    min_detachment_rate: float,
    max_detachment_rate: float,
    n_carriers: int = 1,
) -> np.ndarray:
    """Calculate theoretical PSD for the condensed matter model.

    Input:
        freqs:
            Desired frequencies.
        pulse_magnitude:
            Fixed magnitude of the pulses in the signal.
        capture_rate:
            Rate at which charge carriers are captured.
        min_detachment_rate:
            Minimum expected detachment rate from the capturing potential
        max_detachment_rate:
            Maximum expected detachment rate from the capturing potential
        n_carriers: (default: 1)
            Number of independent charge carriers.

    Output:
        Theoretical estimate of PSD values at the desired frequencies.
    """
    mean_pulse = 1 / capture_rate
    mean_gap = 1 / min_detachment_rate
    if max_detachment_rate > min_detachment_rate:
        mean_gap = np.log(max_detachment_rate / min_detachment_rate) / (
            max_detachment_rate - min_detachment_rate
        )
    nu_bar = 1 / (mean_pulse + mean_gap)

    const_term = n_carriers * (pulse_magnitude**2) * nu_bar

    if max_detachment_rate <= min_detachment_rate:  # detachment_rate is fixed
        const_term = 4 * const_term
        rate_term = capture_rate + min_detachment_rate
        angular_freqs = 2 * np.pi * freqs
        return const_term / (rate_term**2 + angular_freqs**2)

    if capture_rate < max_detachment_rate:  # long pulses assumption valid
        const_term = const_term / max_detachment_rate
        return const_term / freqs

    # long pulses assumption invalid
    const_term = const_term * max_detachment_rate / (capture_rate**2)
    log_freq_term = (np.pi / 2) ** 2 + (
        max_detachment_rate / capture_rate
        - np.log(2 * np.pi * freqs / max_detachment_rate)
    ) ** 2
    return const_term / freqs / log_freq_term
