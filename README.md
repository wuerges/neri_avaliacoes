# Scripts para o Neri

Este repositório tem um script para produzir os relatórios de avaliação do curso de MTM da UFFS.
O script é capaz de ler um ods e produzir os relatórios usando pandas+matplotlib.

## Dependências

Precisa ter o Python 3 e o Pipenv instalados. 
Depois o Pipenv faz o resto.

## Como usar:

```
pipenv install
pipenv run python main.py --arquivo <arquivo.ods>
```