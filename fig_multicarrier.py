from collections import Counter

import matplotlib.gridspec as gridspec  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore
from scipy.stats import binom  # type: ignore


def __get_pmf(data: np.ndarray) -> np.ndarray:
    """Obtain PMF out of data."""
    c = Counter(data)
    n_samples = len(data)
    pmf = np.array([[x, p / n_samples] for x, p in c.items()])
    return pmf[pmf[:, 0].argsort()]


def __get_free_prob(
    desired_T: float,
    capture_rate: float,
    min_detachment_rate: float,
    max_detachment_rate: float,
) -> float:
    """Calculate the probability that selected carrier is free."""
    mean_free_time = 1 / capture_rate
    min_detachment_rate = np.max([min_detachment_rate, 1 / desired_T])
    mean_captured_time = np.log(max_detachment_rate / min_detachment_rate) / (
        max_detachment_rate - min_detachment_rate
    )
    return mean_free_time / (mean_free_time + mean_captured_time)


files = [
    "data/poiss10000.upoiss0_1000.nc1000.multi.seed23567.0.series.csv.gz",
    "data/poiss10000.upoiss0_1000.nc1000.multi.seed23567.0.series.csv",
    "data/poiss10000.upoiss0_1000.nc1000.multi.seed23567.psd.csv",
]

# simulation parameters (needed to obtain nice signal and PMF plots)
dt = 5e-5
n_carriers = 1e3
capture_rate = 1
min_detachment_rate = 0
max_detachment_rate = 1e3

# signal ploting parameters
plot_signal_vals = int(1e3)  # how many signal values to plot
skip_signal_vals = int(1e2)  # plot each x-th value

with PdfPages("figs/multicarrier.pdf") as pdfFile:
    fig = plt.figure(figsize=(4.8, 3.2))
    grid = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[0.75, 1])
    ax1 = fig.add_subplot(grid[0, :])
    ax2 = fig.add_subplot(grid[1, 0])
    ax3 = fig.add_subplot(grid[1, 1])

    ax1.set_ylim([973, 996])
    try:  # try to read gzip file, fallback to raw file; data is reused in 132
        data = np.loadtxt(files[0], delimiter=",")
    except FileNotFoundError:
        data = np.loadtxt(files[1], delimiter=",")
    T = np.arange(0, plot_signal_vals) * (dt * skip_signal_vals)
    ax1.set_ylabel(r"$I(t) / a$")
    ax1.set_xlabel(r"$t$")
    ax1.plot(T, data[: (plot_signal_vals * skip_signal_vals) : skip_signal_vals])
    ax1.text(
        0.95,
        0.9,
        "(a)",
        horizontalalignment="right",
        verticalalignment="center",
        transform=ax1.transAxes,
    )

    ax2.set_xlabel(r"$I / a$")
    ax2.set_ylabel(r"$p(I / a)$")
    # data is read in 131
    pmf = __get_pmf(data)
    prob = __get_free_prob(
        len(data) * dt, capture_rate, min_detachment_rate, max_detachment_rate
    )
    theory_x = np.arange(np.min(data), np.max(data) + 1)
    theory_y = binom.pmf(theory_x, n_carriers, prob)
    ax2.plot(pmf[:, 0], pmf[:, 1], "o")
    ax2.plot(theory_x, theory_y, "k--")
    ax2.text(
        0.95,
        0.9,
        "(b)",
        horizontalalignment="right",
        verticalalignment="center",
        transform=ax2.transAxes,
    )
    del data, pmf, theory_x, theory_y

    ax3.loglog()
    ax3.set_xlabel(r"$f$")
    ax3.set_xticks([1e-3, 1e-1, 1e1, 1e3])
    ax3.set_ylabel(r"$S_N(f)$")
    ax3.set_yticks([1e-5, 1e-3, 1e-1, 1e1, 1e3])
    data = 10 ** np.loadtxt(files[2], delimiter=",")
    ax3.plot(data[:, 0], data[:, 1])
    ax3.plot(data[:, 0], data[:, 2], "k--")
    ax3.text(
        0.95,
        0.9,
        "(c)",
        horizontalalignment="right",
        verticalalignment="center",
        transform=ax3.transAxes,
    )
    del data

    plt.tight_layout()

    pdfFile.savefig(fig)
    plt.close()
