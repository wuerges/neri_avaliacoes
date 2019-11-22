AMBIENTAL = "ambiental"
MATEMATICA = "matematica"

formatos = [AMBIENTAL, MATEMATICA]

import argparse
parser = argparse.ArgumentParser(description='Analisa um odt com respostas do questinário.')

parser.add_argument('arquivos', type=str, nargs='+',
                    help='planilhas a serem analisadas.')

parser.add_argument('--formato', dest='formato', required=True, #action='store_const', const=
                    choices=formatos,
                    help='arquivo ods a ser analisado')

args = parser.parse_args()
