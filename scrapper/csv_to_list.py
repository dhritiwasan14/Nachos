import csv
import pandas as pd

df = pd.read_csv("./links.csv")

links_list = [e[0] for e in df.values]

# print(links_list)
