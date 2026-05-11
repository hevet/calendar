import requests
import re
import json
from bs4 import BeautifulSoup
from html import unescape
from datetime import datetime

URL = "https://www.kalbi.pl/"


def clean(text):
    return unescape(text.strip())


html = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
).text

soup = BeautifulSoup(html, "html.parser")

result = {
    "calendar": "",
    "namedays": "",
    "zodiac": "",
    "officialHolidays": "",
    "holidays": "",
    "proverbs": ""
}


# =====================================================
# DZIEŃ TYGODNIA
# =====================================================

weekday = ""

dayweek = soup.find("div", class_="calCard-day-week")

if dayweek:
    weekday = clean(dayweek.text)


# =====================================================
# DATA
# =====================================================

date_input = soup.find("input", {"name": "data"})

if date_input:
    date = date_input.get("value", "")

    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")

        months = {
            1: "stycznia",
            2: "lutego",
            3: "marca",
            4: "kwietnia",
            5: "maja",
            6: "czerwca",
            7: "lipca",
            8: "sierpnia",
            9: "września",
            10: "października",
            11: "listopada",
            12: "grudnia"
        }

        result["calendar"] = (
            f"{weekday}, "
            f"{dt.day} "
            f"{months[dt.month]} "
            f"{dt.year}"
        )


# =====================================================
# IMIENINY
# =====================================================

section = soup.find("section", class_="calCard-name-day")

result["namedays"] = ""

if section:

    html_section = str(section)

    parts = re.split(r'oraz', html_section, flags=re.IGNORECASE)

    first_part = parts[0]

    soup_part = BeautifulSoup(first_part, "html.parser")

    names = []

    for a in soup_part.find_all("a"):
        names.append(clean(a.text))

    result["namedays"] = ", ".join(names)


# =====================================================
# ZODIAK
# =====================================================

html_text = str(soup)

m = re.search(
    r'Słoneczny znak zodiaku:\s*(.*?)"',
    html_text
)

if m:
    result["zodiac"] = clean(m.group(1))


# =====================================================
# ŚWIĘTA OFICJALNE
# =====================================================

fete = soup.find("div", class_="calCard-fete")

if fete:
    result["officialHolidays"] = clean(fete.text)


# =====================================================
# NIETYPOWE ŚWIĘTA
# =====================================================

holidays = []

section = soup.find("section", class_="calCard-ententa")

if section:
    for a in section.find_all("a"):
        holidays.append(clean(a.text))

result["holidays"] = ". ".join(holidays)


# =====================================================
# PRZYSŁOWIA
# =====================================================

proverbs = []

section = soup.find("section", class_="calCard_proverb")

if section:
    for li in section.find_all("li"):
        proverbs.append(clean(li.text))

result["proverbs"] = " ".join(proverbs)


# =====================================================

with open("calendar.json", "w", encoding="utf-8") as f:
    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )

print("calendar.json generated")
