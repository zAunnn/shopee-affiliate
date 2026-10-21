import os
import re
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
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Product_Name", "Affiliate_Link"])
    
    if df.empty:
        print("ไม่พบข้อมูลสินค้าใน Google Sheets")
        exit(1)

    selected = df.sample(1).iloc[0]
    product_name = str(selected["Product_Name"]).strip()
    shopee_link = str(selected["Affiliate_Link"]).strip()
    
    # ดึงลิงก์รูปภาพและแปลง Google Drive Link เป็น Direct Image Link ให้อัตโนมัติ
    raw_image_url = str(selected.get("Image_File", "")).strip()
    image_url = ""
    
    if raw_image_url and "http" in raw_image_url:
        if "drive.google.com" in raw_image_url:
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', raw_image_url)
            if not match:
                match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', raw_image_url)
            if match:
                file_id = match.group(1)
                image_url = f"https://lh3.googleusercontent.com/d/{file_id}"
        else:
            image_url = raw_image_url

    print(f"สุ่มได้สินค้าสำเร็จ: {product_name}")
    print(f"ลิงก์พิกัด: {shopee_link}")
    print(f"ลิงก์รูปภาพ: {image_url if image_url else 'ไม่พบรูปภาพ'}")

except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 3. สร้างแคปชันด้วย Gemini (ส่งข้อความโพสต์เดียวพร้อมใช้ทันที)
post_text = None
if GEMINI_KEY:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"""
        คุณคือพนักงานป้ายยาสินค้าบน Facebook หน้าที่ของคุณคือเขียนแคปชันขายสินค้า Affiliate
        
        ข้อมูลสินค้า:
        - ชื่อสินค้า: {product_name}
        - ลิงก์สั่งซื้อ: {shopee_link}

        คำสั่งสำคัญมาก:
        1. ให้เขียนออกมาเป็นข้อความโพสต์แคปชันเดียวเท่านั้น
        2. ห้ามทำเป็นตัวเลือก ห้ามมีคำอธิบายเพิ่มเติม
        3. ใส่พาดหัวน่าตื่นเต้น มีอีโมจิ บรรยายจุดเด่นสั้นๆ ใส่ลิงก์พิกัด {shopee_link} และแฮชแท็กท้ายโพสต์ให้เรียบร้อยพร้อมใช้งานทันที
        """
        response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
        post_text = response.text
    except Exception as e:
        print(f"Gemini API แจ้งเตือน: {e} -> ใช้ข้อความสำรองแทน")

if not post_text:
    post_text = f"🔥 ป้ายยาแรง! {product_name}\n\n🛒 พิกัดสั่งซื้อ: {shopee_link}\n\n#Shopee #Affiliate #ของดีบอกต่อ"

# 4. โพสต์ลง Facebook Page (รองรับทั้งแบบมีรูปและไม่มีรูป)
if image_url:
    # โพสต์รูปภาพพร้อมแคปชัน
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "message": post_text,
        "access_token": PAGE_TOKEN
    }
else:
    # โพสต์ข้อความอย่างเดียว (กรณีไม่มีรูป)
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
    payload = {
        "message": post_text,
        "access_token": PAGE_TOKEN
    }

response = requests.post(url, data=payload)
if response.status_code == 200:
    print("โพสต์รูปลง Facebook สำเร็จเรียบร้อย!")
else:
    print(f"Facebook API Error: {response.text}")
    exit(1)
