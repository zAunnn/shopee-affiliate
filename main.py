import os
import csv
import json
import random
import requests
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. อ่านข้อมูลสินค้าทั้งหมด
products = []
with open('products.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        products.append(row)

# 2. โหลดประวัติการโพสต์เดิม
history_file = 'history.json'
posted_products = []
if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        try:
            posted_products = json.load(f)
        except:
            posted_products = []

# 3. กรองเอาเฉพาะสินค้าที่ยังไม่เคยโพสต์
available_products = [p for p in products if p["Product_Name"] not in posted_products]

# ถ้าโพสต์ครบทุกตัวแล้ว ให้รีเซ็ตประวัติเริ่มวนใหม่
if not available_products:
    posted_products = []
    available_products = products

# 4. สุ่มสินค้าจากกลุ่มที่ยังไม่เคยโพสต์
selected_product = random.choice(available_products)
product_name = selected_product["Product_Name"]
shopee_link = selected_product["Affiliate_Link"]
image_url = selected_product["Image_Url"]

print(f"สุ่มได้สินค้า: {product_name}")

# 5. สร้างแคปชันด้วย Gemini
prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate ช้อปปี้ สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hastag ที่เกี่ยวข้อง และอีโมจิให้ดึงดูด น่าซื้อ"
response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
post_text = response.text

# 6. โพสต์ลง Facebook Page
PAGE_ID = os.environ["FB_PAGE_ID"]
FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]
url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
payload = {
    'url': image_url,
    'message': post_text,
    'access_token': FB_PAGE_ACCESS_TOKEN
}

fb_response = requests.post(url, data=payload)
if fb_response.status_code != 200:
    raise Exception(f"โพสต์ไม่สำเร็จ: {fb_response.text}")

print("โพสต์สำเร็จเรียบร้อย!")

# 7. บันทึกประวัติลง history.json
posted_products.append(product_name)
with open(history_file, 'w', encoding='utf-8') as f:
    json.dump(posted_products, f, ensure_ascii=False, indent=4)
