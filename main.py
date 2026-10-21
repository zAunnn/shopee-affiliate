import os
import json
import random
import requests
import pandas as pd
from google import genai

# 1. ตั้งค่า Gemini Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. ใส่ URL CSV ที่ได้จาก Publish to web ของ Google Sheets
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAzqsnuQBZ68r46Occb7QR3gPdd9E99BLJXH2FeyWuSzUQokUHxRIB6LIiMfGYGxTrO0MfxAlMkBSI/pub?gid=1694411054&single=true&output=csv"

# 3. อ่านข้อมูลสินค้าจาก Google Sheets
df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

# แปลงเป็น List of Dicts
products = df.to_dict(orient='records')

# 4. โหลดประวัติการโพสต์จาก history.json
history_file = 'history.json'
posted_products = []
if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        try:
            posted_products = json.load(f)
        except:
            posted_products = []

# 5. กรองสินค้าที่ยังไม่เคยโพสต์ (เทียบจากชื่อสินค้า)
available_products = [p for p in products if str(p.get("Product_Name")) not in posted_products]

if not available_products:
    posted_products = []
    available_products = products

# 6. สุ่มเลือกสินค้า 1 รายการ
selected = random.choice(available_products)
product_name = selected["Product_Name"]
shopee_link = selected["Affiliate_Link"]

# หมายเหตุ: ดึง URL รูปภาพจากไฟล์ที่อัปโหลดใน Google Drive/Form
# (Google Form จะเก็บลิงก์ Google Drive ของรูปภาพไว้ในคอลัมน์รูปภาพ)
drive_file_id = selected["Image_File"].split("id=")[-1]
image_url = f"https://lh3.googleusercontent.com/d/{drive_file_id}"

print(f"สุ่มได้สินค้า: {product_name}")

# 7. สร้างแคปชันด้วย Gemini
prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate ช้อปปี้ สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hastag ที่เกี่ยวข้อง และอีโมจิให้ดึงดูด น่าซื้อ"
response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
post_text = response.text

# 8. โพสต์ลง Facebook Page
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

# 9. บันทึกประวัติ
posted_products.append(str(product_name))
with open(history_file, 'w', encoding='utf-8') as f:
    json.dump(posted_products, f, ensure_ascii=False, indent=4)
