from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

file_path = DATA_DIR / "financials_raw.csv"
clean_file_path = DATA_DIR / "financials_final.csv"

# Load the CSV file
df = pd.read_csv(file_path, encoding="ISO-8859-1")

# Remove the columns that have INVOICE_MONTH 12 and INVOICE_YEAR 2023
df = df[~((df["INVOICE_MONTH"] == 12) & (df["INVOICE_YEAR"] == 2023))]

# Save the modified DataFrame back to the CSV file
df.to_csv(clean_file_path, index=False)
