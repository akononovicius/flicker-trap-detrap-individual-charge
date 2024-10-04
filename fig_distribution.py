import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore


def __get_overall_pdf(
    x: np.ndarray | float, rate_min: float, rate_max: float
) -> np.ndarray | float:
    """Obtain system-wide PDF."""
    min_term = -np.exp(-rate_min * x) * (1 + rate_min * x) / (x**2)
    max_term = -np.exp(-rate_max * x) * (1 + rate_max * x) / (x**2)
    return (max_term - min_term) / (rate_max - rate_min)


def __get_individual_pdf(x: np.ndarray | float, rate: float) -> np.ndarray | float:
    """Obtain individual center PDF."""
    return rate * np.exp(-rate * x)


# parameters for the plot
rate_min = 1e-3
rate_max = 1e1
arbitrary_shift = 10  # additional arbitrary shift to the "individual" PDF curves
show_n_rates = 10  # N individual rates to show

# decide which inividual rates to show
individual_rates = np.logspace(np.log10(rate_min), np.log10(rate_max), num=show_n_rates)

with PdfPages("figs/distribution.pdf") as pdfFile:
    fig = plt.figure(figsize=(2.4, 1.6))
    plt.loglog()

    ax = plt.gca()
    ax.set_xlabel(r"$\tau$")
    ax.set_ylabel(r"$p(\tau)$")
    ax.set_xlim([5e-3, 2e4])
    ax.set_xticks([1e-2, 1e0, 1e2, 1e4])
    ax.set_ylim([1e-13, 1e2])
    ax.set_yticks([1e0, 1e-4, 1e-8, 1e-12])

    tau = np.logspace(-np.log10(rate_max) - 1.5, -np.log10(rate_min) + 1.5)
    overall_pdf = __get_overall_pdf(tau, rate_min, rate_max)
    plt.plot(tau, overall_pdf)

    for gamma_tau in individual_rates:
        weight = rate_min / arbitrary_shift / (rate_max - rate_min)
        individual_pdf = __get_individual_pdf(tau, gamma_tau) * weight
        plt.plot(tau, individual_pdf, "k--")

    pdfFile.savefig(fig)
    plt.close()
