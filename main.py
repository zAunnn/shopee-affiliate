import os
import csv
import random
import requests
from google import genai

# 1. ดึงค่า Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")

# 2. อ่านข้อมูลสินค้าจากไฟล์ products.csv
products = []
with open("products.csv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        products.append(row)

# 3. สุ่มเลือกสินค้า 1 ชิ้นจากตาราง
selected_product = random.choice(products)
product_name = selected_product["Product_Name"]
shopee_link = selected_product["Affiliate_Link"]

print(f"สุ่มได้สินค้า: {product_name}")

# 4. กำหนด Prompt ให้ Gemini เขียนแคปชันตามชื่อสินค้า
prompt = f"""
เขียนแคปชันขายสินค้าสำหรับโพสต์ Facebook Page สั้นๆ น่ารัก ชวนซื้อ
สินค้าคือ: {product_name}
ใส่ Emoji และ Hashtag ที่เกี่ยวข้อง
และปิดท้ายด้วยลิงก์นี้เท่านั้น: {shopee_link}
(คำตอบต้องมีเฉพาะเนื้อหาที่จะโพสต์จริงเท่านั้น ห้ามมีคำนำ ตัวเลือก หรือคำเกริ่นใดๆ)
"""

# 5. เรียกใช้งาน Gemini API
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
)

post_content = response.text.strip()
print("=== Generated Post Content ===")
print(post_content)

# 6. โพสต์ลง Facebook Page
url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
payload = {
    "message": post_content,
    "access_token": PAGE_ACCESS_TOKEN,
}

fb_response = requests.post(url, data=payload)
print("=== Facebook API Response ===")
print(fb_response.json())

if fb_response.status_code == 200:
    print("โพสต์ลง Facebook สำเร็จแล้ว!")
else:
    raise Exception(f"โพสต์ไม่สำเร็จ: {fb_response.text}")
