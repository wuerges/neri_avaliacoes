from pyexcel_ods import get_data
import json
import config
from reporter import processa


data = get_data(config.args.arquivo)

# for k,v in data.items():
processa(data)
