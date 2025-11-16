

import pandas as pd
import numpy as np
from pathlib import Path

file = "/Users/rupaliwaghmare/Documents/DATA ANALYSIS/Task 1/marketing_campaign.csv"

df = pd.read_csv(file, sep=';', encoding='utf-8')

print("Rows, Cols:", df.shape)
print(df.head())
df.info()


df.columns = (
    df.columns.str.strip()
              .str.lower()
              .str.replace(' ', '_')
              .str.replace('-', '_')
)

print("Cleaned Columns:", list(df.columns))

# missing values
missing = df.isnull().sum().sort_values(ascending=False)
print("\nMissing values:\n", missing[missing > 0])

# duplicates
dupes = df.duplicated().sum()
print("Duplicate rows:", dupes)

if dupes > 0:
    df = df.drop_duplicates().reset_index(drop=True)

# ID
if 'id' in df.columns:
    df['id'] = df['id'].astype(str).str.strip()

# age
if 'year_birth' in df.columns:
    df['year_birth'] = pd.to_numeric(df['year_birth'], errors='coerce')
    CURRENT_YEAR = pd.Timestamp.now().year
    df['age'] = CURRENT_YEAR - df['year_birth']
    df.loc[(df['age'] < 10) | (df['age'] > 100), 'age'] = np.nan

# income
if 'income' in df.columns:
    df['income'] = (
        df['income'].astype(str)
        .str.replace('[\$,]', '', regex=True)
        .str.strip()
    )
    df['income'] = pd.to_numeric(df['income'], errors='coerce')

# datetime
if 'dt_customer' in df.columns:
    df['dt_customer'] = pd.to_datetime(df['dt_customer'], errors='coerce', dayfirst=True)
    df['dt_customer_str'] = df['dt_customer'].dt.strftime('%d-%m-%Y')

# Complain column
if 'complain' in df.columns:
    df['complain'] = pd.to_numeric(df['complain'], errors='coerce').fillna(0).astype(int)
    df['complain'] = df['complain'].apply(lambda x: 1 if x > 0 else 0)

text_cols = ['education', 'marital_status']
for c in text_cols:
    if c in df.columns:
        df[c] = df[c].astype(str).str.strip().replace('nan', np.nan)
        df[c] = df[c].str.lower()

# education
if 'education' in df.columns:
    df['education'] = df['education'].replace({
        'basic': 'basic',
        '2n cycle': 'basic',
        'graduation': 'graduation',
        'master': 'master',
        'phd': 'phd'
    })

# marital status
if 'marital_status' in df.columns:
    df['marital_status'] = df['marital_status'].replace({
        'married': 'married',
        'together': 'together',
        'single': 'single',
        'divorced': 'divorced',
        'widow': 'widow',
        'alone': 'alone',
        'absurd': 'absurd',
        'yoLO': 'single',
        'unknown': np.nan
    })

# missing values

num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
cat_cols = df.select_dtypes(include=['object']).columns.tolist()

num_cols = [c for c in num_cols if c not in ['id', 'year_birth']]
cat_cols = [c for c in cat_cols if c not in ['id', 'dt_customer', 'dt_customer_str']]

# median
for c in num_cols:
    if df[c].isnull().sum() > 0:
        df[c] = df[c].fillna(df[c].median())

# "unknown"
for c in cat_cols:
    if df[c].isnull().sum() > 0:
        df[c] = df[c].fillna('unknown')


print("\nRemaining missing values:", df.isnull().sum().sum())
print("Final shape:", df.shape)
print(df.head())

out = Path("cleaned_customer_personality.csv")
df.to_csv(out, index=False)
print("Cleaned dataset saved to:", out.resolve())
