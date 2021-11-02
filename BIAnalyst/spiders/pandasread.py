import pandas as pd
def read_data(self):
    df = pd.read_json('Data.json')

    print(df.to_string())

