import traceback
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import config
from textwrap import wrap
from pathlib import Path
from collections import defaultdict
from natsort import natsorted
import functools

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

@functools.lru_cache
def uniformiza_index(nome):
    # nomes = ['1:Plenamente satisfatório', '2:Satisfatório', '3:Regular', '4:Indiferente', '5:Insatisfatório', '6:Não sei']
    nomes = [ 'Plenamente satisfatório', 'Satisfatório', 'Regular', 'Indiferente', 'Insatisfatório', 'Não sei'
            , "Totalmente", "Muito", "Médio", "Pouco", "Não"
            , "Ótimo", "Muito Bom", "Bom", "Regular", "Ruim"
            , "Sempre", "Frequentemente", "Medianamente", "Raramente", "Nunca"
            ]
    scores = [(distancia(nome, n), n) for n in nomes]
    scores.sort()
    # "\n".join(wrap(scores[0][1], 20))
    if scores[0][0] < (len(nome) * 3 // 4):
        return scores[0][1]
    return nome


def uniformiza_planilha(planilha):
    def uniformiza_celula(cel):
        if str(cel) == 'nan':
            return ""

        try:
            if cel:
                return uniformiza_index(cel)
            return cel
        except:
            traceback.print_exc()
            print(cel)
            exit(0)
    
    return planilha.apply(lambda c : c.apply(uniformiza_celula))


def calcula_indice_geral(aba):
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

def cria_grafico_generico(ccr, fase, curso, nomefig):
    # index_geral = calcula_indice_geral(curso)
    index_geral = list(set(fase.index).union(set(ccr.index)).union(set(curso.index)))

    ind = np.arange(len(index_geral))
    fig, ax = plt.subplots()

    # print("DEBUG=")
    # print(index_geral)
    # print(ccr.index)
    # print(fase.index)


    try:
        legends = []
        if not ccr.empty:
            plot_ccr = ccr[index_geral].fillna(0)
            plot_ccr = plot_ccr / plot_ccr.sum()
            p0 = plt.barh(ind, plot_ccr, height=0.2, label="CCR")
            legends.append((p0[0], 'CCR'))
    except KeyError:
        traceback.print_exc()
        print("key error for 1 question. ignoring")

    if not fase.empty:
        plot_fase = fase[index_geral].fillna(0)
        plot_fase = plot_fase / plot_fase.sum()
        p1 = plt.barh(ind+0.2, plot_fase, height=0.2, label="Fase")
        legends.append((p1[0], 'Fase'))

    if not curso.empty:
        plot_curso = curso[index_geral].fillna(0)
        plot_curso = plot_curso / plot_curso.sum()
        p2 = plt.barh(ind+0.4, plot_curso, height=0.2, label="Curso")
        legends.append((p2[0], 'Curso'))


    # for i, v in enumerate(plot_ccr):
    #     plt.text(v + 3, i + .25, str(v))
    
    ax.set_yticks(ind + 0.4 / 2)
    ax.set_yticklabels(index_geral)

    ax.legend(*zip(*legends))

    # ax.legend((p0[0], p1[0], p2[0]), ('CCR', 'Fase', 'Curso'))
    
    ax.set_xticklabels(['{}%'.format(x) for x in range(0, 110, 10)])
    plt.tight_layout()
    # plt.show()
    # exit(0)

    plt.savefig(nomefig, dpi=120)
    plt.clf()
    plt.close()

def agrupa(data, series):
    # print("agrupa ------------------------------")
    # print(data)
    # print("series name = '{}'".format(series))
    # print("data-series")
    # print(data[series])
    ds = data[series]
    group = ds.groupby(ds).count()
    group = group.drop(['', 'nan'], errors='ignore')

    return group


def extrai_disciplina(txt):
    expr = re.compile(r".*\[(.*)\]")
    # print("extraindo [{}]".format(txt))
    mat = expr.match(txt)
    if mat:
        return mat.group(1)
    return None

def remove_disciplina(txt):
    expr = re.compile(r"(.*)\[.*\]")
    # print("extraindo [{}]".format(txt))
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

def deduplicate(frame):
    dup = frame.columns.duplicated()
    if any(dup):
        frame = frame.loc[:,~frame.columns.duplicated()]
        return frame
    return frame


registro = {}
def unifica_nomes_parecidos(nome):
    global registro
    if not nome in registro:
        for key in registro.keys():
            if distancia(nome, key) < 1+(len(nome) // 6):
                registro[nome] = key
                break
    if not nome in registro:
        registro[nome] = nome
    return registro[nome]


def processa(complete_input):

    items = []

    nome_fases = [x[0] for x in complete_input]
    nome_disciplinas = []

    for filename, data in complete_input:

        if config.args.formato == config.AMBIENTAL:
            df = pd.DataFrame(list(data.values())[0])
            df.columns = df.iloc[0]
            df = df[1:]

            disciplinas = defaultdict(list)
            for txt in df.columns:
                ex = extrai_disciplina(txt)
                d = "Perguntas gerais"
                if ex:
                    d = unifica_nomes_parecidos(ex)

                disciplinas[d].append(txt)
                nome_disciplinas.append(d)

            for k, idx in disciplinas.items():
                tab_disciplina = df[idx]
                tab_disciplina.columns = map(remove_disciplina, tab_disciplina.columns)

                tab_disciplina["disciplina"] = k
                tab_disciplina["fase"] = filename

                for col in tab_disciplina.columns:
                    if col != unifica_nomes_parecidos(col):
                        print("col {} => {}".format(col, unifica_nomes_parecidos(col)))                    
                novo_colunas = [unifica_nomes_parecidos(col) for col in tab_disciplina.columns]
                # for col in tab_disciplina.columns:
                    # if not col in registro_nome_colunas:
                    #     for past in registro_nome_colunas.keys():
                    #         if distancia(col, past) < (len(col) * 2 // 4):
                    #             registro_nome_colunas[col] = past
                    #             print("-----------------------------\nrenomeando: {} => {}".format(col, past))
                    #             break
                        
                    # if not col in registro_nome_colunas:
                    #     registro_nome_colunas[col] = col
                    # novo_colunas.append(registro_nome_colunas[col])

                tab_disciplina.columns = novo_colunas
                tab_disciplina = deduplicate(tab_disciplina)

                # exit(0)
                items.append(tab_disciplina)


        elif config.args.formato == config.MATEMATICA:
            for k, v in data.items():
                df = pd.DataFrame(v)
                # remove a primeira linha do conjunto de dados
                df.columns = df.iloc[0]
                df = df[1:]
                df = fix_index(k, df)
                df = uniformiza_planilha(df)
                df["disciplina"] = k
                df["fase"] = "?"
                items.append(deduplicate(df.fillna(0)))

    nome_disciplinas = list(set(nome_disciplinas))

    complete = pd.concat(items)
    
    complete = uniformiza_planilha(complete)

    for nf in nome_fases:
        for nd in nome_disciplinas:
            processa_planilha(nd, nf, complete)

def processa_planilha(nome_disciplina, nome_fase, complete):

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

        data_fase = complete[complete["fase"] == nome_fase]
        data = complete[complete["disciplina"] == nome_disciplina]
        data = data.drop(["fase", "disciplina"], axis=1)

        for i, series in enumerate(natsorted(d for d in data)):
            if series:
                print("Pergunta:", series)

                group_planilha = agrupa(complete, series)
                group_fase = agrupa(data_fase, series)
                group = agrupa(data, series)

                nomefig = Path("figura{}.svg".format(i))
                if group.empty:
                    doc.add_pergunta_textual(series, ["Nao houve respostas."])

                elif testa_resposta_textual(group):
                    doc.add_pergunta_textual(series, group.index)

                else:
                    cria_grafico_generico(group, group_fase, group_planilha, nomefig)
                    doc.add_pergunta(series, (nomefig, group.sum(), group_fase.sum(), group_planilha.sum()))
                # break

        with open("index.html", "w") as f:
            f.write(doc.texto())
        os.chdir("..")
    except:
        print("falhei processando {}".format(nome_disciplina))
        traceback.print_exc()
        os.chdir(original)
        exit(0)


