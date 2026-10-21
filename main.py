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
image_url = selected_product["Image_Url"]  # <--- เพิ่มบรรทัดนี้ดึงลิงก์รูปภาพจาก CSV

print(f"สุ่มได้สินค้า: {product_name}")

# 4. กำหนด Prompt ให้ Gemini เขียนแคปชั่นตามชื่อสินค้า
prompt = f"""
เขียนแคปชั่นขายสินค้าสำหรับโพสต์ Facebook Page สั้นๆ น่ารัก ชวนซื้อ
สินค้าคือ: {product_name}

โดยให้ใช้โครงสร้างการเว้นบรรทัดดังนี้:
[หัวข้อดึงดูดสายตาพร้อม Emoji]

[เนื้อหาจุดเด่นสินค้า 2-3 บรรทัด สั้นกระชับ]

🛒 พิกัดช้อปตรงนี้เลย👇
{shopee_link}

ใส่ Hashtag ที่เกี่ยวข้อง

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

# 6. โพสต์รูปภาพพร้อมแคปชั่นลง Facebook Page
url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/photos"
payload = {
    "caption": post_content,      # เปลี่ยนจาก message เป็น caption
    "url": image_url,             # ใส่ลิงก์รูปภาพสินค้า
    "access_token": PAGE_ACCESS_TOKEN
}
fb_response = requests.post(url, data=payload)
print("=== Facebook API Response ===")
print(fb_response.json())

if fb_response.status_code == 200:
    print("โพสต์ลง Facebook สำเร็จแล้ว!")
else:
    raise Exception(f"โพสต์ไม่สำเร็จ: {fb_response.text}")
