import pandas as pd

def processa(k, v):
    data = pd.Series(v)
    print(k, data)