import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap
from pathlib import Path

import os

from documento import Documento

def processa(k, v):
    data = pd.DataFrame(v)
    new_header = data.iloc[0]
    data = data[1:]
    data.columns = new_header

    print("Disciplina", k)
    original = os.getcwd()
    try:
        doc = Documento(k)
        try:
            os.mkdir(k)
        except FileExistsError:
            pass
        os.chdir(k)
        
        for i, series in enumerate(data):
            print("Pergunta:", series)
            ds = data[series]
            group = ds.groupby(ds).count()

            # print("printing group")
            # print(group)

            labs = ["\n".join(wrap(c, 20)) for c in group.index]

            plt.pie(group, labels=labs)
            # plt.title(series)
            nomefig = Path("figura{}.png".format(i))
            plt.savefig(nomefig)
            plt.clf()

            doc.add_pergunta(series, nomefig)

        with open("index.html", "w") as f:
            f.write(doc.texto())
        os.chdir("..")
    except:
        print("falhei processando {}".format(k))
        os.chdir(original)


        # plt.show()


        # ax = group[subg].plot.pie(subplots=True)
        # ax[0].get_figure().savefig("myplot.png")
        # print(ax[0].get_figure())
        # exit(0)
