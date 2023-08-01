import numpy as np


def convert_to_series(
    t_start: float,
    t_end: float,
    t_step: float,
    pulse_durations: np.ndarray | list,
    gap_durations: np.ndarray | list,
) -> np.ndarray:
    """Convert from pulse/gap duration representation to time series representation.

    Input:
        t_start:
            Start time of the time series.
        t_end:
            End time of the time series.
        t_step:
            Discretization step for the time series.
        pulse_durations:
            List of pulse durations.
        gap_durations:
            List of gap durations.

    Output:
        Two dimensional array containing two columns of values. First one is
        for time, second one is for the value (0 or 1) observed at that time.
    """
    pulse_starts = (
        np.cumsum(pulse_durations) + np.cumsum(gap_durations) - pulse_durations
    )

    times = np.arange(t_start, t_end, t_step)
    series = np.array([__get_value(t, pulse_starts, pulse_durations) for t in times])
    return np.vstack((times, series)).T


def __get_value(
    t: float,
    pulse_starts: np.ndarray,
    pulse_durations: np.ndarray | list,
) -> float:
    """Get the value of SNORP at a given time t.

    Input:
        t:
            Desired time moment.
        pulse_starts:
            List of pulse start times.
        pulse_durations:
            List of pulse durations.

    Output:
        0 or 1 depending on if t falls within gap or pulse.
    """
    if t < pulse_starts[0]:
        return 0
    pulse_id = int(np.argmin(pulse_starts < t)) - 1
    if pulse_id < 0:
        pulse_id = len(pulse_starts) - 1
    if t < (pulse_starts[pulse_id] + pulse_durations[pulse_id]):
        return 1
    return 0
