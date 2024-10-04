import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

from lib.series import convert_to_series

colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

series = convert_to_series(0, 4.45, 0.01, [1, 1.5, 1], [0.005, 1, 0.75])

with PdfPages("figs/explanation.pdf") as pdfFile:
    fig = plt.figure(figsize=(2.4, 1.6))

    ax = plt.gca()
    ax.grid(visible=False)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$I_1(t)$")
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r"$0$", r"$a$"])
    ax.set_xticks([0, 2, 4.25])
    ax.set_xticklabels([r"$t_{i-1}$", r"$t_i$", r"$t_{i+1}$"])

    plt.plot(series[:, 0], series[:, 1], linestyle="-", color=colors[0])
    plt.plot([4.45, 5], [1, 1], linestyle=":", color=colors[0])

    ax.annotate(r"$\theta_i$", [0.5, 0.5], ha="center", va="center", xycoords="data")
    ax.annotate(
        "",
        xy=(0, 0.6),
        xycoords="data",
        xytext=(1, 0.6),
        textcoords="data",
        arrowprops=dict(arrowstyle="<->"),
    )
    ax.annotate(r"$\tau_i$", [1.5, 0.5], ha="center", va="center", xycoords="data")
    ax.annotate(
        "",
        xy=(1, 0.4),
        xycoords="data",
        xytext=(2, 0.4),
        textcoords="data",
        arrowprops=dict(arrowstyle="<->"),
    )
    ax.annotate(
        r"$\theta_{i+1}$", [2.75, 0.5], ha="center", va="center", xycoords="data"
    )
    ax.annotate(
        "",
        xy=(2, 0.6),
        xycoords="data",
        xytext=(3.5, 0.6),
        textcoords="data",
        arrowprops=dict(arrowstyle="<->"),
    )
    ax.annotate(
        r"$\tau_{i+1}$", [3.875, 0.5], ha="center", va="center", xycoords="data"
    )
    ax.annotate(
        "",
        xy=(3.5, 0.4),
        xycoords="data",
        xytext=(4.25, 0.4),
        textcoords="data",
        arrowprops=dict(arrowstyle="<->"),
    )

    pdfFile.savefig(fig)
    plt.close()
