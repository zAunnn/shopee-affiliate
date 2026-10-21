import os
import random
import pandas as pd
import requests
from google import genai

# 1. โหลด Environment Variables ให้ตรงกับ GitHub Actions
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
PAGE_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# 2. อ่านข้อมูลจาก Google Sheets (ใช้ลิงก์ CSV เดิมของคุณ)
CSV_URL = "docs.google.com/spreadsheets/d/e/2PACX-1vRAzqsnuQBZ68r46Occb7QR3gPdd9E99BLJXH2FeyWuSzUQokUHxRIB6LIiMfGYGxTrO0MfxAlMkBSI/pub?gid=1694411054&single=true&output=csv"  # ถ้าในโค้ดเดิมมีอยู่แล้ว ใช้ของเดิมได้เลยครับ

try:
    df = pd.read_csv(CSV_URL)
    selected = df.sample(1).iloc[0]
    product_name = str(selected.get("Product_Name", "สินค้าแนะนำ"))
    shopee_link = str(selected.get("Affiliate_Link", "https://shopee.co.th"))
    print(f"สุ่มได้สินค้า: {product_name}")
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 3. สร้างแคปชัน (มีระบบสำรองอัตโนมัติ ป้องกัน Error 429 ของ Gemini)
post_text = None
if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hashtag และอีโมจิดึงดูดน่าซื้อ"
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        post_text = response.text
    except Exception as e:
        print(f"Gemini API ใช้งานไม่ได้ชั่วคราว (Quota เต็ม): {e} -> ใช้ข้อความสำรองแทน")

# ถ้า Gemini พังหรือโควตาหมด ให้ใช้ข้อความนี้แทนทันที บอทจะได้ไม่หยุดทำงาน
if not post_text:
    post_text = f"🔥 ป้ายยาแรง! {product_name}\n\n🛒 พิกัดสั่งซื้อ: {shopee_link}\n\n#Shopee #Affiliate #ของดีบอกต่อ"

# 4. โพสต์ลง Facebook Page
url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
payload = {
    "message": post_text,
    "access_token": PAGE_TOKEN
}

response = requests.post(url, data=payload)
if response.status_code == 200:
    print("โพสต์ลง Facebook สำเร็จเรียบร้อย!")
else:
    print(f"Facebook API Error: {response.text}")
    exit(1)
