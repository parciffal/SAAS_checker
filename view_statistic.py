import pandas as pd
from config import config
result = {
        0: "Esim",
        3: "100% Saas",
        -3: "100% Pbn",
        1: "25% Saas",
        -1: "25% Pbn",
        2: "50% Saas",
        -2: "50% Pbn"
    }
df = pd.read_csv(config.local.csv_file_dir)
checked_count = df[df['checked'] == True].shape[0]
not_checked = df[df['checked'] == False].shape[0]
saashand = df[df['result'] == "100% Saas"].shape[0]
saasfive = df[df['result'] == "50% Saas"].shape[0]
saastwo = df[df['result'] == "25% Saas"].shape[0]
pbnhand = df[df['result'] == "100% Pbn"].shape[0]
pbnfive = df[df['result'] == "50% Pbn"].shape[0]
pbntwo = df[df['result'] == "25% Pbn"].shape[0]
esim = df[df['result'] == "Esim"].shape[0]


print(f"Checked: {checked_count}")
print(f"Not Checked: {not_checked}")

print(f"100% Saas: {saashand}")
print(f"100% Pbn: {pbnhand}")

print(f"50% Saas: {saasfive}")
print(f"50% Pbn: {pbnfive}")

print(f"25% Saas: {saastwo}")
print(f"25% Pbn: {pbntwo}")

print(f"Esim : {esim}")
