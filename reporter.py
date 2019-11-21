import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textwrap import wrap
from pathlib import Path

import os

from documento import Documento


def distancia(str1, str2):
    cache = [[-1 for x in str2] for y in str1]

    def disted(str1, i, str2, j):
        if len(str1) == i:
            return len(str2) - j
        if len(str2) == j:
            return len(str1) - i
        if cache[i][j] != -1:
            return cache[i][j]
        
        if str1[i] == str2[j]:
            return disted(str1, i+1, str2, j+1)

        cache[i][j] = 1+min(disted(str1, i, str2, j+1), disted(str1, i+1, str2, j))
        return cache[i][j]

    return disted(str1, 0, str2, 0)

def uniformiza_index(nome):
    nomes = ['Indiferente', 'Insatisfatório', 'Não sei', 'Plenamente satisfatório', 'Regular', 'Satisfatório']
    scores = [(distancia(nome, n), n) for n in nomes]
    scores.sort()
    return "\n".join(wrap(scores[0][1], 15))


def uniformiza_planilha(planilha):
    def tamanho_certo(idx):
        return 1 <= len(idx.split()) <= 2
    def uniformiza_celula(cel):
        if cel:
            return uniformiza_index(cel) if tamanho_certo(cel) else cel
        return cel
    
    return planilha.apply(lambda c : c.apply(uniformiza_celula))

def cria_grafico(aba, planilha, nomefig):
    # labs = ["\n".join(wrap(c, 20)) for c in aba.index]
    print(aba)
    print(aba.index)

    index_geral = [idx for idx in planilha.index if 1 <= len(idx.split()) <= 2]

    ind = np.arange(len(index_geral))
    fig, ax = plt.subplots()
    ax.bar(ind, aba[index_geral].fillna(0), width=0.3, label="planilha")
    ax.bar(ind+0.3, planilha[index_geral].fillna(0), width=0.3, label="coluna")
    ax.set_xticklabels(index_geral)


    plt.show()


    print(planilha.index)
    # plt.pie(group, labels=labs)

    plt.savefig(nomefig)
    plt.clf()

def agrupa_planilha(planilha):

    ds = pd.concat(planilha[series] for series in planilha)
    group = ds.groupby(ds).count()
    return group


def processa(k, v):
    
    # constroi um data frame a partir de um arquivo
    data = pd.DataFrame(v)

    # remove a primeira linha do conjunto de dados
    new_header = data.iloc[0]
    data = data[1:]
    data.columns = new_header

    print("Disciplina", k)
    original = os.getcwd()
    # try:
    doc = Documento(k)
    try:
        os.mkdir(k)
    except FileExistsError:
        pass
    os.chdir(k)


    data = uniformiza_planilha(data)
    group_planilha = agrupa_planilha(data)

    for i, series in enumerate(data):
        print("Pergunta:", series)
        ds = data[series]
        group = ds.groupby(ds).count()

        nomefig = Path("figura{}.png".format(i))
        cria_grafico(group, group_planilha, nomefig)

        doc.add_pergunta(series, nomefig)
        break

    with open("index.html", "w") as f:
        f.write(doc.texto())
    exit(0)
    os.chdir("..")
    # except:
    #     print("falhei processando {}".format(k))
    #     os.chdir(original)


