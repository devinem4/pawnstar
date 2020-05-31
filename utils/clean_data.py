import pandas as pd


raw = pd.read_excel("./data/rpt.xlsx", header=9, skipfooter=15)

# remove all columns with only null data
raw = raw.dropna(axis=1, how="all")

raw.columns = [
    col.lower().replace(": ", "_").replace(" ", "_").replace("#", "")
    for col in raw.columns
]

# row 0 is a second header row so drop it
raw = raw.drop(0, axis=0)

# any row without something in the `ticket` field is garbage
raw = raw[pd.notnull(raw["ticket"])]

# excel sheet has two different types of data in the `ticket` col
# 1. The ticket number (good)
# 2. The item description (bad -- needs to be moved)
#
# step 1 -- copy `ticket` to `ticket_num` for valid ticket numbers (identified using
#     `isdigit()`). We'll use ffill to copy those `ticket_num` down.
raw.loc[raw["ticket"].astype(str).str.isdigit(), "ticket_num"] = raw[
    raw["ticket"].astype(str).str.isdigit()
]["ticket"]
raw["ticket_num"] = raw["ticket_num"].fillna(method="ffill")

# step 2 -- separate the `ticket` rows from the `item_description` rows
tickets = raw[raw["ticket"].astype(str).str.isdigit()]
item_descs = raw[~raw["ticket"].astype(str).str.isdigit()]

# step 3 -- rename item_descs columns to represent what is really stored in those cols.
item_desc_col_map = {
    "ticket": "item_description",
    "date_in": "bin",
    "date_out": "quantity",
    "svg_chg_due": "item_amount",
    "amount": "resale_amount",
}

item_descs = item_descs.rename(columns=item_desc_col_map)
item_descs = item_descs[list(item_desc_col_map.values()) + ["ticket_num"]]

# step 4 -- rejoin the data back together
tickets = tickets.set_index("ticket_num")
item_descs = item_descs.set_index("ticket_num")
pawn_df = tickets.join(item_descs, how="outer")


pawn_df.to_csv("./data/clean.csv", index=False)
