import os
import pandas as pd
import requests
from google import genai

# 1. โหลด Environment Variables
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
PAGE_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# 2. อ่านข้อมูลจาก Google Sheets CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAzqsnuQBZ68r46Occb7QR3gPdd9E99BLJXH2FeyWuSzUQokUHxRIB6LIiMfGYGxTrO0MfxAlMkBSI/pub?gid=1694411054&single=true&output=csv"

try:
    df = pd.read_csv(CSV_URL)
    
    # ตัดเว้นวรรคหน้า-หลัง ของชื่อคอลัมน์ทั้งหมดเพื่อป้องกัน KeyError
    df.columns = df.columns.str.strip()
    
    # กรองเฉพาะแถวที่มีชื่อสินค้าและลิงก์จริง
    df = df.dropna(subset=["Product_Name", "Affiliate_Link"])
    
    if df.empty:
        print("ไม่พบข้อมูลสินค้าใน Google Sheets")
        exit(1)

    # สุ่มเลือกสินค้า 1 รายการ
    selected = df.sample(1).iloc[0]
    product_name = str(selected["Product_Name"]).strip()
    shopee_link = str(selected["Affiliate_Link"]).strip()
    
    print(f"สุ่มได้สินค้าสำเร็จ: {product_name}")
    print(f"ลิงก์พิกัด: {shopee_link}")

except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 3. สร้างแคปชันด้วย Gemini (พร้อมระบบ fallback หากโควตาเต็ม)
post_text = None
if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hashtag และอีโมจิดึงดูดน่าซื้อ"
        response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
        post_text = response.text
    except Exception as e:
        print(f"Gemini API แจ้งเตือน: {e} -> ใช้ข้อความสำรองแทน")

# ข้อความสำรอง (ใช้ค่าจริงจาก Google Sheets)
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
