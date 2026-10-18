import csv
import os
import random
from google import genai

# เรียกใช้ Gemini API Key จาก Secret
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
  raise ValueError("ไม่พบ GEMINI_API_KEY ในระบบ Secrets")

client = genai.Client(api_key=api_key)


# อ่านข้อมูลสินค้าจาก products.csv
def get_random_product():
  products = []
  with open("products.csv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
      products.append(row)

  if not products:
    return None
  return random.choice(products)


# สุ่มสินค้ามา 1 ชิ้น
product = get_random_product()

if product:
  prompt = f"""
    ช่วยเขียนแคปชันรีวิวสินค้าสำหรับโพสต์ลงโซเชียลมีเดียเพื่อขายสินค้า Affiliate
    สินค้า: {product['Product_Name']}
    ลิงก์สั่งซื้อ: {product['Affiliate_Link']}

    คำแนะนำการเขียน:
    - เขียนให้น่าสนใจ ดึงดูดสายตา มีการใส่อิโมจิประกอบ
    - เน้นจุดเด่นสินค้าแบบสั้นๆ กระชับ
    - สรุปสั้นๆ และมี Call to Action เชิญชวนให้กดลิงก์สั่งซื้อ
    - ใส่แฮชแท็กที่เกี่ยวข้อง 3-5 อัน
    """

  response = client.models.generate_content(
      model="gemini-3.8-flash", contents=prompt
  )

  print("=== Generated Caption ===")
  print(response.text)
else:
  print("ไม่พบข้อมูลสินค้าใน products.csv")
