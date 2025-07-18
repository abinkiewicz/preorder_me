from clarifai.client.model import Model
from clarifai.client.user import User
from pdf2image import convert_from_path

#z pdf do zdj
pages = convert_from_path('katalog_producenta.pdf', dpi=300)

for i, page in enumerate(pages):
    page.save(f'strona_{i+1}.jpg', 'JPEG')

#detekcja ze zdj

PAT = "TWÓJ_PAT"
user = User(auth_token=PAT)

model_apparel = Model(user, model_id="general-image-apparel-recognition")
model_color = Model(user, model_id="color")
model_ocr = Model(user, model_id="text-recognition")  # Model OCR Clarifai

image_path = "tshirt_red_with_id.jpg"

with open(image_path, "rb") as f:
    image_bytes = f.read()

# 1. Klasyfikacja ubrań
res_apparel = model_apparel.predict_by_bytes(image_bytes)
top_class = res_apparel["outputs"][0]["data"]["concepts"][0]["name"]

# 2. Klasyfikacja koloru
res_color = model_color.predict_by_bytes(image_bytes)
top_color = res_color["outputs"][0]["data"]["colors"][0]["w3c"]["name"]

# 3. OCR — odczyt tekstu (np. ID produktu)
res_ocr = model_ocr.predict_by_bytes(image_bytes)
texts = res_ocr["outputs"][0]["data"]["regions"]

# Zbieramy wszystkie wykryte teksty
detected_texts = []
for region in texts:
    for line in region["data"]["text"]["lines"]:
        detected_texts.append(line["text"])

# Zakładamy, że ID produktu jest jednym z tych tekstów (np. wybierz pierwszy lub filtruj)
product_id = detected_texts[0] if detected_texts else "BRAK_ID"

print(f"ID produktu: {product_id}")
print(f"Rodzaj ubrania: {top_class}")
print(f"Dominujący kolor: {top_color}")