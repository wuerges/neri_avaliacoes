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
    nomes = ['1:Plenamente satisfatório', '2:Satisfatório', '3:Regular', '4:Indiferente', '5:Insatisfatório', '6:Não sei']
    scores = [(distancia(nome, n), n) for n in nomes]
    scores.sort()
    # "\n".join(wrap(scores[0][1], 20))
    return scores[0][1]


def uniformiza_planilha(planilha):
    def tamanho_certo(idx):
        return 1 <= len(idx.split()) <= 2
    def uniformiza_celula(cel):
        if cel:
            return uniformiza_index(cel) if tamanho_certo(cel) else cel
        return cel
    
    return planilha.apply(lambda c : c.apply(uniformiza_celula))


def calcula_indice_geral(aba, planilha):
    tot = set(list(aba.index) + ['1:Plenamente satisfatório', '2:Satisfatório', '3:Regular', '4:Indiferente', '5:Insatisfatório', '6:Não sei'])
    index_geral = list(tot)
    index_geral.sort()
    index_geral.reverse()
    return index_geral

def testa_resposta_textual(aba):
    for idx in aba.index:
        if len(idx.split()) > 10:
            return True
    return False

# def testa_grafico_generico(aba, planilha):
#     index_geral = calcula_indice_geral(aba, planilha)
    
#     for idx in aba.index:
#         if not idx in index_geral:
#             return False
#     return True

# def cria_grafico_especifico(aba, nomefig):
#     plt.barh(aba.index, aba)
#     plt.tight_layout()
#     plt.savefig(nomefig)
#     plt.clf()


def cria_grafico_generico(aba, planilha, nomefig):
    index_geral = calcula_indice_geral(aba, planilha)

    ind = np.arange(len(index_geral))
    fig, ax = plt.subplots()

    print("DEBUG=")
    print(aba)
    plot_aba = aba[index_geral].fillna(0)
    plot_aba = plot_aba / plot_aba.sum()

    plot_planilha = planilha[index_geral].fillna(0)
    plot_planilha = plot_planilha / plot_planilha.sum()

    p1 = plt.barh(ind, plot_aba, height=0.3, label="Disciplina")
    p2 = plt.barh(ind+0.3, plot_planilha, height=0.3, label="Geral")

    # for i, v in enumerate(plot_aba):
    #     plt.text(v + 3, i + .25, str(v))
    
    ax.set_yticks(ind + 0.3 / 2)
    ax.set_yticklabels(index_geral)
    ax.legend((p1[0], p2[0]), ('Disciplina', 'Geral'))
    
    ax.set_xticklabels(['{}%'.format(x) for x in range(0, 110, 10)])
    plt.tight_layout()
    plt.savefig(nomefig)
    plt.clf()
    plt.close()

def agrupa_planilha(planilha):

    ds = pd.concat(planilha[series] for series in planilha)
    group = ds.groupby(ds).count()
    return group


def processa(k, v):
    
    # constroi um data frame a partir de um arquivo
    data = pd.DataFrame(v)

    # remove a primeira linha do conjunto de dados
    data.columns = data.iloc[0]
    data = data[1:]

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
        if group.empty:
            doc.add_pergunta_textual(series, ["Nao houve respostas."])

        elif testa_resposta_textual(group):
            doc.add_pergunta_textual(series, group.index)

        else:
        # elif testa_grafico_generico(group, group_planilha):
            cria_grafico_generico(group, group_planilha, nomefig)
            # print("SOMA GRUPO=", group.sum())
            # print(group)
            doc.add_pergunta(series, (nomefig, group.sum()))
        # else:
        #     cria_grafico_especifico(group, nomefig)
        #     doc.add_pergunta(series, nomefig)

        # break

    with open("index.html", "w") as f:
        f.write(doc.texto())
    os.chdir("..")
    # except:
    #     print("falhei processando {}".format(k))
    #     os.chdir(original)


