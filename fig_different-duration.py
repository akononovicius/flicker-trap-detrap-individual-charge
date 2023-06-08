import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages  # type: ignore

files = [
    "data/poiss10000.upoiss0_1000.seed18557.psd.csv",
    "data/poiss10000.upoiss0_1000.seed16022.psd.csv",
    "data/poiss10000.upoiss0_1000.seed11921.psd.csv",
]

with PdfPages("figs/different-duration.pdf") as pdfFile:
    fig = plt.figure(figsize=(3, 2))
    plt.loglog()

    ax = plt.gca()
    ax.set_xlabel(r"$f$")
    ax.set_ylabel(r"$S_1(f)$")
    ax.set_ylim([1e-11, 3e3])
    ax.set_yticks([1e-10, 1e-6, 1e-2, 1e2])
    ax.set_xticks([1e-7, 1e-5, 1e-3, 1e-1, 1e1, 1e3])

    for fN in files:
        data = 10 ** np.loadtxt(fN, delimiter=",")
        plt.plot(data[::2, 0], data[::2, 1])

    plt.plot(data[:, 0], data[:, 2], "k--")

    pdfFile.savefig(fig)
    plt.close()
