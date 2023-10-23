#! /usr/bin/env python3

import sys
import pandas as pd
# mpl.use('Agg')
# mpl.rcParams['lines.linewidth'] = 2
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
import os
from pathlib import Path

os.chdir(Path(__file__).parent)


def getData(csv_file, x):
    # load data in pandas DataFrame
    df = pd.read_csv(csv_file, sep=";", header=None)

    twodslice = df.loc[df[0] == x, [1, 2, 3]]
    velocitymap = []
    for i in range(4, 22):
        row = twodslice.loc[twodslice[1] == i, 3].values.tolist()
        velocitymap.append(row)
    return velocitymap


# #plt.style.use("ggplot")
# plt.figure(figsize=(5.44,4 * 0.8))
plt.rcParams['font.size'] = 15
plt.rcParams["savefig.dpi"] = 250
plt.rcParams["savefig.pad_inches"] = 0.05
my_map = "Paired"
fig, ax = plt.subplots()

filedata = getData('../data/filter4step1000.csv', 5)
plt.imshow(filedata, cmap='plasma', interpolation='none', vmin=0, vmax=1.5)

plt.colorbar(label='velocity')# fraction=0.035#, pad=0.02)

plt.xlabel('Macroscopic cell along z')
plt.ylabel('Macroscopic cell along y')
ax.xaxis.set_ticks_position('top')
ax.xaxis.set_label_position('top')
#plt.xticks([])
#plt.yticks([])
plt.xticks([x*3 for x in range(6)]+[17],[(x*3)+4 for x in range(6)]+[21], fontsize=10)
plt.yticks([x*3 for x in range(6)]+[17],[(x*3)+4 for x in range(6)]+[21], fontsize=10)
# plt.axis('off')
# plt.tick_params(top=False, bottom=False, left=False, right=False)

fig_width, fig_height = plt.gcf().get_size_inches()
fig.set_size_inches(6, 5, forward=True)
# plt.title("MultiMD + Filtering - 128 Instances")
plt.savefig("../figures/heatmapfilter4.png", format="png", bbox_inches='tight')
if '--no-show' not in sys.argv:
    plt.show()

exit(0)
