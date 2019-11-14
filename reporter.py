import pandas as pd
import matplotlib.pyplot as plt

from textwrap import wrap

def processa(k, v):
    data = pd.DataFrame(v)
    new_header = ["\n".join(wrap(c, 50)) for c in data.iloc[0]]
    data = data[1:]
    data.columns = new_header
    for series in data:        
        print("series = ", series)
        ds = data[series]
        group = ds.groupby(ds).count()

        print("printing group")
        print(group)

        labs = ["\n".join(wrap(c, 20)) for c in group.index]

        plt.pie(group, labels=labs)
        plt.title(series)
        plt.show()
        # ax = group[subg].plot.pie(subplots=True)
        # ax[0].get_figure().savefig("myplot.png")
        # print(ax[0].get_figure())
        # exit(0)
