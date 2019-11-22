import traceback
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import config
from textwrap import wrap
from pathlib import Path
from collections import defaultdict

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
        cel = str(cel)
        if cel:
            return uniformiza_index(cel) if tamanho_certo(cel) else cel
        return cel
    
    return planilha.apply(lambda c : c.apply(uniformiza_celula))


def calcula_indice_geral(aba, planilha):
    if config.args.formato == config.AMBIENTAL:
        opt1 = ["Totalmente", "Muito", "Médio", "Pouco", "Não"]
        opt1.reverse()
        opt2 = ["Ótimo", "Muito Bom", "Bom", "Regular", "Ruim"]
        opt2.reverse()
        opt3 = ["Sempre", "Frequentemente", "Medianamente", "Raramente", "Nunca"]
        opt3.reverse()
        if set(aba.index).intersection(set(opt1)):
            return opt1
        if set(aba.index).intersection(set(opt2)):
            return opt2
        if set(aba.index).intersection(set(opt3)):
            return opt3
        return aba.index
    else:
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

def cria_grafico_generico(aba, planilha, nomefig):
    index_geral = calcula_indice_geral(aba, planilha)

    ind = np.arange(len(index_geral))
    fig, ax = plt.subplots()

    # print("DEBUG=")
    # print(index_geral)
    # print(aba.index)
    # print(planilha.index)
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

def agrupa(data, series):
    print("agrupa ------------------------------")
    print(data)
    print("series name = '{}'".format(series))
    print("data-series")
    print(data[series])
    ds = data[series]
    group = ds.groupby(ds).count()
    return group


def extrai_disciplina(txt):
    expr = re.compile(r".*\[(.*)\]")
    print("extraindo [{}]".format(txt))
    mat = expr.match(txt)
    if mat:
        return mat.group(1)
    return None

def remove_disciplina(txt):
    expr = re.compile(r"(.*)\[.*\]")
    print("extraindo [{}]".format(txt))
    mat = expr.match(txt)
    if mat:
        return mat.group(1)
    return None

def fix_index(k, data):
    expr = re.compile(r".*\[(.*)\]")

    def f(perg):
        mat = expr.match(perg)
        if mat:
            return mat.group(1)
        return perg

    data.columns = map(f, data.columns)
    return data

def processa(complete_input):
    
    items = []

    nome_fases = [x[0] for x in complete_input]
    nome_disciplinas = []

    for filename, data in complete_input:

        if config.args.formato == config.AMBIENTAL:
            df = pd.DataFrame(list(data.values())[0])
            df.columns = df.iloc[0]
            df = df[1:]
            print("COLUNAS")
            print(df.columns)

            disciplinas = defaultdict(list)
            for txt in df.columns:
                d = extrai_disciplina(txt)
                if d:
                    disciplinas[d].append(txt)
                    nome_disciplinas.append(d)

            for k, idx in disciplinas.items():
                tab_disciplina = df[idx]
                print("ANTES", tab_disciplina.columns)
                tab_disciplina.columns = map(remove_disciplina, tab_disciplina.columns)
                print("DEPOIS", tab_disciplina.columns)

                tab_disciplina["disciplina"] = k
                tab_disciplina["fase"] = filename
                items.append(tab_disciplina)


        elif config.args.formato == config.MATEMATICA:
            for k, v in data.items():
                df = pd.DataFrame(v)
                # remove a primeira linha do conjunto de dados
                df.columns = df.iloc[0]
                df = df[1:]
                df = fix_index(k, df)
                df = uniformiza_planilha(df)
                items.append((k, df))

    nome_disciplinas = list(set(nome_disciplinas))
    complete = pd.concat(items)
    
    for nf in nome_fases:
        for nd in nome_disciplinas:
            processa_planilha(nd, nf, complete)



def processa_planilha(nome_disciplina, nome_fase, complete):
    print("processa_planilha -------------------------------")
    print(nome_disciplina)
    print(nome_fase)
    print(complete)

    # constroi um data frame a partir de um arquivo


    print("Disciplina", nome_disciplina)
    original = os.getcwd()
    try:
        doc = Documento(nome_disciplina)
        try:
            os.mkdir(nome_disciplina)
        except FileExistsError:
            pass
        os.chdir(nome_disciplina)

        print("TESTANDO ILOC")
        print(nome_disciplina)
        data = complete[complete["disciplina"] == nome_disciplina]
        data_fase = complete[complete["fase"] == nome_fase]

        for i, series in enumerate(data):
            if series:
                print("Pergunta:", series)

                group_planilha = agrupa(complete, series)
                group_fase = agrupa(data_fase, series)
                group = agrupa(data, series)

                nomefig = Path("figura{}.png".format(i))
                if group.empty:
                    doc.add_pergunta_textual(series, ["Nao houve respostas."])

                elif testa_resposta_textual(group):
                    doc.add_pergunta_textual(series, group.index)

                else:
                # elif testa_grafico_generico(group, group_planilha):
                    cria_grafico_generico(group, group_fase, nomefig)
                    # print("SOMA GRUPO=", group.sum())
                    # print(group)
                    doc.add_pergunta(series, (nomefig, group.sum(), group_planilha.sum()))
                # else:
                #     cria_grafico_especifico(group, nomefig)
                #     doc.add_pergunta(series, nomefig)

                # break

        with open("index.html", "w") as f:
            f.write(doc.texto())
        os.chdir("..")
    except:
        print("falhei processando {}".format(nome_disciplina))
        traceback.print_exc()
        os.chdir(original)


