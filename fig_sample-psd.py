import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

files = [
    "data/poiss10000.upoiss1_10000.seed6288.psd.csv",
]

colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

with PdfPages("figs/sample-psd.pdf") as pdfFile:
    fig = plt.figure(figsize=(3, 2))
    plt.loglog()

    ax = plt.gca()
    ax.set_xlabel(r"$f$")
    ax.set_ylabel(r"$S_1(f)$")
    ax.set_xticks([1e-5, 1e-3, 1e-1, 1e1, 1e3, 1e5])
    ax.set_yticks([1e-10, 1e-7, 1e-4, 1e-1, 1e2])

    for c, fN in zip(colors, files):
        data = 10 ** np.loadtxt(fN, delimiter=",")
        plt.plot(data[:, 0], data[:, 1], color=c)
        plt.plot(data[:, 0], data[:, 2], "k--")

    pdfFile.savefig(fig)
    plt.close()
