import pandas as pd
import numpy as np

def read_toyota(file_name: str) -> pd.DataFrame:
    "Read the csv file_name, do basic prepping"
    df = pd.read_csv(file_name)
    df = df.drop(columns=['Id', 'Model', 'Mfg_Month', 'Mfg_Year', 'Cylinders'])
    df['Fuel_Type'] = df['Fuel_Type'].astype('category')
    df['Color'] = df['Color'].astype('category')
    # df['Gears'] = df['Gears'].astype('category')
    # df['Doors'] = df['Doors'].astype('category')

    df.loc[df['CC'] == 16000, 'CC'] = 1600
    df.rename(columns={'Age_08_04': 'Age'}, inplace=True)

    for col in df.columns:
        if df[col].nunique() == 2:
            df[col] = df[col].astype('bool')

    df['Combined_Color'] = df.apply(
        lambda row:
        f'Met_{row["Color"]}' if row['Met_Color']
        else row['Color'], axis=1
    ).astype('category')

    df['Age^2'] = df['Age']**2
    df['KM^2'] = df['KM']**2
    df['eAge'] = np.exp(-df['Age'])
    df['eKM'] = np.exp(-df['KM'])
    df['Weight^2'] = df['Weight'] ** 2
    return df

# df = pd.get_dummies(df, drop_first=True)
