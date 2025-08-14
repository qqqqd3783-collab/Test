from delete_protect import set_password, prompt_login, protect_path, protect_self

# 1) ตั้งรหัสผ่าน (ปรับค่าได้ตามต้องการ)
set_password("1234")

# 2) บล็อกไฟล์ตัวเอง (+ โฟลเดอร์ตัวเอง) ตั้งแต่เริ่มรัน
protect_self(protect_parent=True)

# 3) บังคับล็อกอินก่อนเข้าโหมดควบคุม
if not prompt_login():
    raise SystemExit

print("💻 พร้อมรับคำสั่ง")
print("   - ใช้: B <path>   (บล็อกไม่ให้ลบ path นั้น)")
print("   - ใช้: EXIT        (ออกโปรแกรม)")
print()

while True:
    try:
        cmd = input("> ").strip()
        if not cmd:
            continue

        low = cmd.lower()

        if low.startswith("b "):               # B <path>
            path = cmd[2:].strip()
            if path:
                protect_path(path)
            else:
                print("❗ กรุณาใส่ path ด้วย เช่น: B C:/ห้ามลบ")
        elif low in ("exit", "quit"):
            print("👋 ออกจากโปรแกรมแล้ว")
            break
        else:
            print("❓ ไม่รู้จักคำสั่งนี้ (ใช้ B <path> หรือ EXIT)")
    except KeyboardInterrupt:
        print("\n👋 ออกจากโปรแกรมแล้ว")
        break
