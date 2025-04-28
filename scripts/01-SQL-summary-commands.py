import sqlite3
import pandas as pd

conn = sqlite3.connect('edu_data.db')
cursor = conn.cursor()

# Read CSVs
arg_df = pd.read_csv("../data/ARG_edu_data.csv")
bra_df = pd.read_csv("../data/BRA_edu_data.csv")
ven_df = pd.read_csv("../data/VEN_edu_data.csv")
chl_df = pd.read_csv("../data/CHL_edu_data.csv")

# Cleaning series names
new_values = ["primary", "secondary", "tertiary"]
arg_df.loc[:len(new_values)-1, 'series'] = new_values
bra_df.loc[:len(new_values)-1, 'series'] = new_values
ven_df.loc[:len(new_values)-1, 'series'] = new_values
chl_df.loc[:len(new_values)-1, 'series'] = new_values


# Rename 'series' to 'series_name' to avoid double series column
for df in [arg_df, bra_df, ven_df, chl_df]:
    if 'series' in df.columns:
        df.rename(columns={'series': 'series_name'}, inplace=True)

# Melt function
def melt_edu(df, country):
    melted = df.melt(id_vars=['series_name'], 
                     value_vars=[f'YR{year}' for year in range(2000, 2023)],
                     var_name='year', 
                     value_name='enrollment')
    melted['year'] = melted['year'].str.replace('YR', '')
    melted['country'] = country
    return melted

# Melt all datasets
arg_melted = melt_edu(arg_df, 'ARG')
bra_melted = melt_edu(bra_df, 'BRA')
ven_melted = melt_edu(ven_df, 'VEN')
chl_melted = melt_edu(chl_df, 'CHL')

# Concatenate into one big table
all_edu = pd.concat([arg_melted, bra_melted, ven_melted, chl_melted])

# Write to SQL
all_edu.to_sql('edu_data', conn, if_exists='replace', index=False)

print(" ")
print("Count of years with enrollment data per country per level:") 

cursor.execute('''
    SELECT country, series_name, COUNT(enrollment) FROM edu_data WHERE enrollment IS NOT NULL GROUP BY country, series_name ORDER BY country, series_name;
''')
for row in cursor.fetchall():
    print(row)

print(" ")
print("RANGE enrollment per country per level (first and last years not null):") 

cursor.execute('''
    WITH non_nulls AS (SELECT country, series_name, year, enrollment FROM edu_data WHERE enrollment IS NOT NULL)
    SELECT country, series_name, MIN(year) AS first_year, MAX(year) AS last_year FROM non_nulls
    GROUP BY country, series_name ORDER BY country, series_name ''')
for row in cursor.fetchall():
    print(row)


print(" ")
print("Max enrollment per country per level:") 

cursor.execute('''
    WITH ranked AS (SELECT country, series_name, year, enrollment, ROW_NUMBER() OVER (PARTITION BY country, series_name ORDER BY enrollment DESC) as rn FROM edu_data WHERE enrollment IS NOT NULL)
    SELECT country, series_name, year, enrollment AS max_enrollment FROM ranked WHERE rn = 1 
    ORDER BY country, series_name''')
for row in cursor.fetchall(): print(row)

print(" ")
print("Min enrollment per country per level:") 

cursor.execute('''
    WITH ranked AS (SELECT country, series_name, year, enrollment, ROW_NUMBER() OVER (PARTITION BY country, series_name ORDER BY enrollment ASC) as rn FROM edu_data WHERE enrollment IS NOT NULL)
    SELECT country, series_name, year, enrollment AS max_enrollment FROM ranked WHERE rn = 1 
    ORDER BY country, series_name''')
for row in cursor.fetchall(): print(row)
