import os
import random
import requests
from google import genai

# 1. ดึงค่า Secrets จาก GitHub
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")

# 2. รายการลิงก์สินค้า Shopee Affiliate (แปะลิงก์จริงเพิ่มต่อลงในนี้ได้เรื่อยๆ เลยครับ)
shopee_links = [
    "https://s.shopee.co.th/1BFamJiLW",
    "https://s.shopee.co.th/7VHGWj5Th0",
    "https://s.shopee.co.th/7fagj54SOO",
]

# สุ่มหยิบมา 1 ลิงก์สำหรับการโพสต์รอบนี้
shopee_link = random.choice(shopee_links)

# 3. กำหนด Prompt ให้ Gemini เขียนเฉพาะแคปชันโพสต์จริง
prompt = f"""
เขียนแคปชันขายสินค้าสำหรับโพสต์ Facebook Page สั้นๆ น่ารัก ชวนซื้อ 
ใส่ Emoji และ Hashtag ที่เกี่ยวข้อง
และปิดท้ายด้วยลิงก์นี้เท่านั้น: {shopee_link}
(คำตอบต้องมีเฉพาะเนื้อหาที่จะโพสต์จริงเท่านั้น ห้ามมีคำนำ ตัวเลือก หรือคำเกริ่นใดๆ)
"""

# 4. เรียกใช้งาน Gemini API
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

post_content = response.text.strip()
print("=== Generated Post Content ===")
print(post_content)

# 5. โพสต์ลง Facebook Page ผ่าน Graph API
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
