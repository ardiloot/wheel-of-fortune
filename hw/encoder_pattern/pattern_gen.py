import numpy as np
import matplotlib.pylab as plt
from matplotlib.patches import Wedge, Circle

if __name__ == "__main__":
    fig, ax = plt.subplots(1, 1, figsize=(0.0393701 * 420.0, 0.0393701 * 594.0))

    # Sectors
    r0 = 140.0
    dr = 13.0
    pad_r = 1.0
    center = (0.0, 0.0)
    n_sectors = 16
    for i in range(n_sectors):
        gray = i ^ (i >> 1)
        for j, p in enumerate([8, 4, 2, 1]):
            active = gray & p
            if not active:
                continue

            r_center = r0 + j * dr
            r = r_center + 0.5 * dr - 0.5 * pad_r
            width = dr - pad_r

            dth = 360.0 / n_sectors
            th1 = i * dth
            th2 = th1 + dth
            ax.add_patch(
                Wedge(center, r, th1, th2, width=width, color="k", ec="r", lw=0.0)
            )

    # Speed
    n_sectors = 128
    r_center = r0 + 4 * dr
    r = r_center + 0.5 * dr - 0.5 * pad_r
    width = dr - pad_r
    for i in range(n_sectors):
        if i % 2 == 0:
            continue

        dth = 360.0 / n_sectors
        th1 = i * dth - 0.5 * dth
        th2 = th1 + dth
        ax.add_patch(Wedge(center, r, th1, th2, width=width, color="k", ec="r", lw=0.0))

    # Lines
    r_lines = 500  # r0 - 20
    for i, th in enumerate(np.radians(np.linspace(0, 360, 32, endpoint=False))):
        x, y = r_lines * np.sin(th), r_lines * np.cos(th)
        ax.plot([0.0, x], [0.0, y], lw=0.2, color="k")

    # Circles
    for r in [13.5, 28, 40, 50, 130, 210]:
        ax.add_patch(Circle(center, radius=r, ec="k", fill=False, lw=0.2))

    # Holes
    r_holes = 23.0
    for th in np.radians(np.linspace(0, 360, 4, endpoint=False)):
        x, y = r_holes * np.sin(th), r_holes * np.cos(th)
        ax.add_patch(Circle((x, y), radius=0.50 * 5.5, ec="k", fill=False, lw=0.2))

    ax.set_aspect("equal")
    ax.set_xlim(-210, 210)
    ax.set_ylim(-0.5 * 594, 0.5 * 594)
    ax.axis("off")
    fig.tight_layout(pad=0)

    fig.savefig(r"pattern.pdf")

    plt.show()
