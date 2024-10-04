import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

files = [
    "data/poiss10000.upoiss0_1000.seed16022.psd.csv",
    "data/poiss10000.upoiss0_1000.seed23245.psd.csv",
]

colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

with PdfPages("figs/different-duration-big-r.pdf") as pdfFile:
    fig = plt.figure(figsize=(2.4, 1.6))
    plt.loglog()

    ax = plt.gca()
    ax.set_xlabel(r"$f$")
    ax.set_ylabel(r"$S_1(f)$")
    ax.set_ylim([1e-11, 3e3])
    ax.set_yticks([1e-10, 1e-6, 1e-2, 1e2])
    ax.set_xticks([1e-5, 1e-3, 1e-1, 1e1, 1e3])

    data = 10 ** np.loadtxt(files[0], delimiter=",")
    plt.plot(data[::2, 0], data[::2, 1], color=colors[1])
    data = 10 ** np.loadtxt(files[1], delimiter=",")
    plt.plot(data[:, 0], data[:, 1], color=colors[5])

    plt.plot(data[:, 0], data[:, 2], "k--")

    pdfFile.savefig(fig)
    plt.close()
