from pyexcel_ods import get_data
import json
import config
from reporter import processa


data = [(arq, get_data(arq)) for arq in config.args.arquivos]

# for k,v in data.items():
processa(data)
