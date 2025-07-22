import pandas 
import csv

df = pandas.read_csv("data.csv")
df2 = pandas.read_csv("data2.csv")



f1 = pandas.DataFrame(set(zip(df["ID"], df["Cena"], df["Link"])), columns=["ID", "Cena", "Link"]).sort_values(axis=0, by='ID',ascending=True)
f2 = pandas.DataFrame(set(zip(df2["ID"], df2["Cena"], df2["Link"])), columns=["ID", "Cena", "Link"]).sort_values(axis=0, by='ID',ascending=True)

#print(f1, f2)

diff = f1.merge(f2, how='outer', indicator=True).query("_merge != 'both'").rename(columns={'_merge': 'Zmiana'})

diff['Zmiana'] = diff['Zmiana'].map({
    'left_only': 'Dodano',
    'right_only': 'Zakończono'
})

header = ['ID', "Zmiana", "Cena", "Link"]

diff = diff[header]

html_table = diff.to_html(index=False, escape=False, border=1)

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

with open("table.html", "a") as f:
  f.write(html_body)
  
diff = diff.to_csv('changes.csv', index=False)


#print(added.to_csv(index=False))
#print(expired.to_csv(index=False))
