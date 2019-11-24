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
from utils import distancia
import functools
import logging

import os

from documento import Documento


def uniformiza_planilha(planilha):
    return planilha.apply(lambda c : c.apply(unifica_nomes_parecidos))

# def calcula_indice_geral(aba):
#     if config.args.formato == config.AMBIENTAL:
#         opt1 = ["Totalmente", "Muito", "Médio", "Pouco", "Não"]
#         opt1.reverse()
#         opt2 = ["Ótimo", "Muito Bom", "Bom", "Regular", "Ruim"]
#         opt2.reverse()
#         opt3 = ["Sempre", "Frequentemente", "Medianamente", "Raramente", "Nunca"]
#         opt3.reverse()
#         if set(aba.index).intersection(set(opt1)):
#             return opt1
#         if set(aba.index).intersection(set(opt2)):
#             return opt2
#         if set(aba.index).intersection(set(opt3)):
#             return opt3
#         return aba.index
#     else:
#         tot = set(list(aba.index) + ['1:Plenamente satisfatório', '2:Satisfatório', '3:Regular', '4:Indiferente', '5:Insatisfatório', '6:Não sei'])
#         index_geral = list(tot)
#         index_geral.sort()
#         index_geral.reverse()
#         return index_geral

def testa_resposta_textual(aba):
    for idx in aba.index:
        if len(idx.split()) > 10:
            return True
    return False

def cria_grafico_generico(ccr, fase, curso, nomefig):
    # index_geral = calcula_indice_geral(curso)
    index_geral = list(natsorted(set(fase.index).union(set(ccr.index)).union(set(curso.index))))
    # index_geral.remove('')
    logging.info("INDEX GERAL={}".format(index_geral))

    ind = np.arange(len(index_geral)-1)
    fig, ax = plt.subplots()

    # print("DEBUG=")
    # print(index_geral)
    # print(ccr.index)
    # print(fase.index)

    # import pdb; pdb.set_trace()

    try:
        legends = []
        # if not ccr.empty:
        plot_ccr = ccr[index_geral].fillna(0).drop('')
        plot_ccr = plot_ccr / plot_ccr.sum()
        # import pdb; pdb.set_trace()
        p0 = plt.barh(ind, plot_ccr, height=0.2, label="CCR")
        legends.append((p0[0], 'CCR'))

    # if not fase.empty:
        plot_fase = fase[index_geral].fillna(0).drop('')
        plot_fase = plot_fase / plot_fase.sum()
        p1 = plt.barh(ind+0.2, plot_fase, height=0.2, label="Fase")
        legends.append((p1[0], 'Fase'))

    # if not curso.empty:
        plot_curso = curso[index_geral].fillna(0).drop('')
        plot_curso = plot_curso / plot_curso.sum()
        p2 = plt.barh(ind+0.4, plot_curso, height=0.2, label="Curso")
        legends.append((p2[0], 'Curso'))

    except:
        traceback.print_exc()
        import pdb; pdb.set_trace()

    # for i, v in enumerate(plot_ccr):
    #     plt.text(v + 3, i + .25, str(v))
    
    ax.set_yticks(ind + 0.4 / 2)
    index_geral.remove('')
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
    # group = group.drop(['', 'nan'], errors='ignore')

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
    if not nome:
        return nome
    global registro
    try:
        if not nome in registro:
            for key in registro.keys():
                if distancia(nome, key) < 1+(len(nome) // 6):
                    logging.info("Renomeando: {} => {}".format(nome, key))
                    registro[nome] = key
                    break
        if not nome in registro:
            registro[nome] = nome
        return registro[nome]
    except TypeError:
        return nome



def processa(complete_input):

    items = []

    nome_fases = defaultdict(set)
    # nome_disciplinas = []

    for filename, data in complete_input:

        if config.args.formato == config.AMBIENTAL:
            df = pd.DataFrame(list(data.values())[0])
            df.columns = df.iloc[0]
            df = df[1:]
            df = df.drop([''], axis=1, errors='ignore')
            df = df.drop(['Timestamp'], axis=1, errors='ignore')
            df = df.drop([None], axis=1, errors='ignore')
            # df = uniformiza_planilha(df)

            disciplinas = defaultdict(list)
            for txt in df.columns:
                ex = extrai_disciplina(txt)
                d = "Perguntas gerais"
                if ex:
                    d = unifica_nomes_parecidos(ex)

                disciplinas[d].append(txt)

            for k, idx in disciplinas.items():
                tab_disciplina = df[idx]
                tab_disciplina.columns = map(remove_disciplina, tab_disciplina.columns)
                
                # tab_disciplina = uniformiza_planilha(tab_disciplina)

                tab_disciplina["disciplina"] = k
                tab_disciplina["fase"] = filename
                nome_fases[filename].add(k)

                # for col in tab_disciplina.columns:
                #     if col != unifica_nomes_parecidos(col):
                #         print("col {} => {}".format(col, unifica_nomes_parecidos(col)))                    
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

    complete = pd.concat(items)
    
    complete = complete.drop([''], axis=1, errors='ignore')
    complete = complete.drop(['Timestamp'], axis=1, errors='ignore')
    complete = complete.drop([None], axis=1, errors='ignore')

    for nf in nome_fases:
        for nd in nome_fases[nf]:
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
        data = data.drop(['disciplina', 'fase'], axis=1)
        
        for d in data:
            logging.info("SERIES ={}".format(d))
        for i, series in enumerate(natsorted(d for d in data)):
            if series:
                print("Pergunta:", series)

                group_planilha = agrupa(complete, series)
                group_fase = agrupa(data_fase, series)
                group = agrupa(data, series)
                # import pdb; pdb.set_trace()

                nomefig = Path("figura{}.svg".format(i))
                if group.empty:
                    doc.add_pergunta_textual(series, ["Nao houve respostas."])

                elif testa_resposta_textual(group):
                    doc.add_pergunta_textual(series, group.index)

                else:
                    def tot(g):
                        return g.drop([''], errors='ignore').sum()
                    cria_grafico_generico(group, group_fase, group_planilha, nomefig)
                    doc.add_pergunta(series, (nomefig, tot(group), tot(group_fase), tot(group_planilha)))
                # break

        with open("index.html", "w") as f:
            f.write(doc.texto())
        os.chdir("..")
    except:
        print("falhei processando {}".format(nome_disciplina))
        traceback.print_exc()
        import pdb; pdb.set_trace()
        os.chdir(original)
        exit(0)


