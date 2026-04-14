from datetime import datetime, timedelta
from bs4 import BeautifulSoup # to parse .htmls more easily
import pandas as pd
import requests
import time

URL = "https://www.tiak.com.tr/icerik/cek.php"

headers = {
  "Referer": "https://www.tiak.com.tr/tablolar",
  "Origin": "https://www.tiak.com.tr"
}

payload = {
  "nere": "tablo",
  "lang": "tr",
  "url": "http://www.tiak.com.tr/",
  "dosya": "Top10 5+"
}

# Fetches data for a specific day
def fetch_specified_day(date):
  current_payload = payload.copy()
  current_payload["tarih"] = date

  res = requests.post(URL, data = current_payload, headers = headers)

  soup = BeautifulSoup(res.text, "html.parser")
  table = soup.find("table")

  rows = []
  for tr in table.find_all("tr"):
    cols = []
    for td in tr.find_all(["td", "th"]):
        s = td.get_text(strip = True)
        cols.append(s)

    if cols:
      rows.append(cols)

  df = pd.DataFrame(rows[1:], columns = rows[0])

  df.columns = ["rank", "programme", "channel", "start_time", "finish_time", "rating", "share" ] # translation from Turkish

  df["date"] = pd.to_datetime(date, format = "%m.%d.%Y")

  return df


# from december 1st, to march 31st ==> 3 months worth of data  
#TODO expand to start of season
start_date = datetime(2026, 1, 1) 
finish_date = datetime(2026, 3, 31)

# Stores every day's df
dfs = []

current = start_date

while current <= finish_date:
  date = f"{current.month}.{current.day}.{current.year}"

  df_day = fetch_specified_day(date)

  if df_day is not None:
      dfs.append(df_day)

  time.sleep(0.8) # pause to not get 404 from the website
  current += timedelta(days = 1)

# Combine the DFs.
df = pd.concat(dfs, ignore_index = True)

df.to_csv("../data/raw/raw_tiak_data.csv", index = False)
