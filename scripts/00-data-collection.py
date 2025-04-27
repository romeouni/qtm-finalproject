import wbgapi as wb
import pandas as pd

indicators = ['SE.PRM.ENRR', 'SE.SEC.ENRR', 'SE.TER.ENRR']
countries = ['BRA', 'ARG', 'CHL', 'VEN']

for country in countries:
    data = wb.data.DataFrame(indicators, economy=country, time=range(2000, 2023), labels=True)
    data.reset_index(inplace=True)

    filename = f'../data/{country}_edu_data.csv'
    data.to_csv(filename, index=False)