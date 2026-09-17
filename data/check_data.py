import pandas as pd

df = pd.read_csv("data/complaints.csv")

print("Dataset shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())