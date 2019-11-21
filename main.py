from pyexcel_ods import get_data
import argparse
import json
from reporter import processa

parser = argparse.ArgumentParser(description='Analisa um odt com respostas do questinário.')
parser.add_argument('--arquivo', dest='arquivo', required=True, #action='store_const', const=
                    help='arquivo ods a ser analisado')

args = parser.parse_args()


print(args.arquivo)


data = get_data(args.arquivo)

# for k,v in data.items():
processa(data)
