'''
PreorderMe v1:
- uploading a fragment of the catalog - photo of the page with socks in .png format,
- using Chat GPT (result in table form + class?)
- verification - EDA (describe whether the model made a mistake, etc.)

'''

#Importy

import json
from pathlib import Path
import base64
from getpass import getpass
from openai import OpenAI
import pandas as pd
import streamlit as st
from dotenv import dotenv_values, load_dotenv
import re

#OPENAI pass - zrobić przez .env
env = dotenv_values(".env")
load_dotenv()

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

#Przygotowanie obrazka
image_path = "milano_socks.png"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

image_data[:100]

def prepare_image_for_open_ai(image_path):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:image/png;base64,{image_data}"


#Zapytanie do GPT
response = openai_client.chat.completions.create(
    # model="gpt-4o",
    model="gpt-4o-mini",
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
Odczytaj informacie o produkcie ze zdjęcia katalogu. Potrzebuję tabelki z informacjami o tych produktach: rodzaj ubrania (np. koszulka, spodenki, buty, skarpetki), 
kolor (z kolorów podstawowych, np. kolory tęczy, np. niebieski - nie musi być błękitny, lazurowy itd.), numer katalogowy produktu, cena.
Dane przedstaw w formacie json. Przedstaw same dane, bez dodatkowych komentarzy.
"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": prepare_image_for_open_ai(image_path),
                        "detail": "high"
                    },
                },
            ],
        }
    ],
)


content = response.choices[0].message.content
match = re.search(r"\[\s*{.*?}\s*\]", content, re.DOTALL)

if match:
    print("Znaleziony fragment JSON:", match.group(0))

data = json.loads(match.group(0))

#Tworzenie df
df = pd.DataFrame(data)
print(df)