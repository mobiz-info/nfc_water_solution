import pandas as pd

# Load files
df1 = pd.read_excel("S43 old.xlsx")   # correct file
df2 = pd.read_excel("S43 live.xlsx")     # file to check



KEY = "Customer ID"
AMOUNT_COL = "Outstanding Amount"   # 🔴 change if name is different

# Keep ONLY required columns
df1 = df1[[KEY, AMOUNT_COL]]
df2 = df2[[KEY, AMOUNT_COL]]   # Bottles & Coupons ignored automatically

# Remove duplicate customer_id (important)
df1 = df1.drop_duplicates(subset=[KEY])
df2 = df2.drop_duplicates(subset=[KEY])

# Set index
df1.set_index(KEY, inplace=True)
df2.set_index(KEY, inplace=True)

# -----------------------------
# 1️⃣ Missing in Excel-2
# -----------------------------
missing_in_2 = df1.loc[~df1.index.isin(df2.index)]
missing_in_2.to_excel("missing_customers.xlsx")

# -----------------------------
# 2️⃣ Extra in Excel-2
# -----------------------------
# extra_in_2 = df2.loc[~df2.index.isin(df1.index)]
# extra_in_2.to_excel("extra_customers.xlsx")

# -----------------------------
# 3️⃣ Outstanding amount changed
# -----------------------------
common_ids = df1.index.intersection(df2.index)

changed = df1.loc[common_ids].compare(df2.loc[common_ids])
changed.to_excel("changed_outstanding.xlsx")

print("✅ Outstanding comparison completed")
