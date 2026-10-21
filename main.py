import os
import csv
import random
import requests
from google import genai

# 1. ตั้งค่า Client ของ Gemini
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. อ่านข้อมูลสินค้าจาก products.csv
products = []
with open('products.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        products.append(row)

# 3. สุ่มเลือกสินค้า 1 ชิ้นจากตาราง
selected_product = random.choice(products)
product_name = selected_product["Product_Name"]
shopee_link = selected_product["Affiliate_Link"]
image_url = selected_product["Image_Url"]

print(f"สุ่มได้สินค้า: {product_name}")

# 4. ให้ Gemini สร้างแคปชัน
prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate ช้อปปี้ สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hastag ที่เกี่ยวข้อง และอีโมจิให้ดึงดูด น่าซื้อ"

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=prompt
)
post_text = response.text
print("=== Generated Post Content ===")
print(post_text)

# 5. โพสต์รูปภาพพร้อมแคปชันไปยัง Facebook Page
PAGE_ID = os.environ["FB_PAGE_ID"]
FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]

url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
payload = {
    'url': image_url,
    'message': post_text,
    'access_token': FB_PAGE_ACCESS_TOKEN
}

fb_response = requests.post(url, data=payload)
print("=== Facebook API Response ===")
print(fb_response.text)

if fb_response.status_code != 200:
    raise Exception(f"โพสต์ไม่สำเร็จ: {fb_response.text}")
else:
    print("โพสต์สำเร็จเรียบร้อย!")
