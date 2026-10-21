import os
import csv
import random
import requests
from google import genai

# ตั้งค่า Client ของ Gemini
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. อ่านข้อมูลสินค้าจาก products.csv
products = []
with open('products.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        products.append(row)

# 2. สุ่มเลือกสินค้า 1 ชิ้นจากตาราง
selected_product = random.choice(products)
product_name = selected_product["Product_Name"]
shopee_link = selected_product["Affiliate_Link"]
image_url = selected_product["Image_Url"]

print(f"สุ่มได้สินค้า: {product_name}")

# 3. ให้ Gemini สร้างแคปชัน
prompt = f"เขียนแคปชันโพสต์ Facebook ขายสินค้า Affiliate ช้อปปี้ สำหรับสินค้า: {product_name} พร้อมลิงก์พิกัด: {shopee_link} ใส่ hastag ที่เกี่ยวข้อง และอีโมจิให้ดึงดูด น่าซื้อ"

response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents=prompt
)
post_text = response.text
print("=== Generated Post Content ===")
print(post_text)

# 4. ดึงชื่อไฟล์รูปภาพจาก URL (เช่น shoes-xtep.jpg)
image_filename = image_url.split('/')[-1]

# 5. ส่งรูปภาพและแคปชันตรงๆ ไปยัง Facebook Graph API
PAGE_ID = os.environ["FB_PAGE_ID"]
FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]

if os.path.exists(image_filename):
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
    payload = {
        'caption': post_text,
        'access_token': FB_PAGE_ACCESS_TOKEN
    }
    with open(image_filename, 'rb') as img_file:
        files = {
            'source': img_file
        }
        fb_response = requests.post(url, data=payload, files=files)
        print("=== Facebook API Response ===")
        print(fb_response.text)
        
        if fb_response.status_code != 200:
            raise Exception(f"โพสต์ไม่สำเร็จ: {fb_response.text}")
        else:
            print("โพสต์สำเร็จเรียบร้อย!")
else:
    raise Exception(f"ไม่พบไฟล์รูปภาพ: {image_filename}")
