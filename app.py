'''
PreorderMe v1:
- uploading a fragment of the catalog - photo of the page with socks in .png format,
- using Chat GPT (result in table form + class?)
- verification - EDA (describe whether the model made a mistake, etc.)

'''

#Imports

import json
from pathlib import Path
import base64
from getpass import getpass
from openai import OpenAI
import pandas as pd
import streamlit as st
from dotenv import dotenv_values, load_dotenv
import re

#OPENAI pass
env = dotenv_values(".env")
load_dotenv()

openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

#Image preparing
image_path = "milano_socks.png"

def prepare_image_for_open_ai(image_path):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:image/png;base64,{image_data}"


#GPT request
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
Read the product information from the catalog photo. I need a table with information about these products: type of clothing (e.g., T-shirt, shorts, shoes, socks), 
color (from basic colors, e.g., rainbow colors, e.g., blue—it does not have to be sky blue, azure, etc.), product catalog number, price.
Present the data in json format. Present the data itself, without additional comments.
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


#Reading and cleaning the response
content = response.choices[0].message.content
match = re.search(r"\[\s*{.*?}\s*\]", content, re.DOTALL)
data = json.loads(match.group(0))

#Creating dataframe
df = pd.DataFrame(data)
print(df)