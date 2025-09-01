import pandas as pd

def compare_files(new_file, old_file):    
    df_new = pd.read_csv(new_file)
    df_old = pd.read_csv(old_file)
    
    df_new["ID"] = df_new["ID"].astype(str).str.strip()
    df_old["ID"] = df_old["ID"].astype(str).str.strip()

    merged = df_new.merge(df_old, on="ID", how="outer", suffixes=("_new", "_old"))

    def classify(row):
        if pd.isna(row["Cena_new"]) and not pd.isna(row["Cena_old"]):  # brak w nowym -> zakończono
            return "Zakończono"
        elif pd.isna(row["Cena_old"]) and not pd.isna(row["Cena_new"]):  # brak w starym -> dodano
            return "Dodano"
        else:
            if row["Cena_new"] != row["Cena_old"]:
                return "Zmiana ceny"
            elif row["Link_new"] != row["Link_old"]:
                return None  # tylko zmiana linku -> ignorujemy
            else:
                return None  # brak zmian

    merged["Zmiana"] = merged.apply(classify, axis=1)

    # przygotowanie kolumn Cena i Link w zależności od przypadku
    def choose_value(row, col):
        if row["Zmiana"] == "Zakończono":
            return row[f"{col}_old"]
        else:
            return row[f"{col}_new"]

    merged["Cena"] = merged.apply(lambda r: choose_value(r, "Cena"), axis=1)
    merged["Link"] = merged.apply(lambda r: choose_value(r, "Link"), axis=1)

    # zostaw tylko potrzebne kolumny
    diff = merged[merged["Zmiana"].notna()][["ID", "Zmiana", "Cena", "Link"]]

    return diff


# porównaj obie pary
diff_single = compare_files("single.csv", "single_old.csv")
diff_multi = compare_files("multi.csv", "multi_old.csv")

# scal wyniki
diff_all = pd.concat([diff_single, diff_multi], ignore_index=True)

# eksport HTML
html_table = diff_all.to_html(index=False, escape=False, border=1)

html_body = f"""
<html>
  <head>
    <meta charset="utf-8">
    <style>
      table {{
        border-collapse: collapse;
        width: 100%;
        font-family: Arial, sans-serif;
      }}
      th, td {{
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
      }}
      th {{
        background-color: #f2f2f2;
      }}
    </style>
  </head>
  <body>
    {html_table}
  </body>
</html>
"""

with open("table.html", "w", encoding="utf-8") as f:
    f.write(html_body)

# eksport CSV
diff_all.to_csv("changes.csv", index=False)
