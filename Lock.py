import os
import ctypes
import subprocess
import sys
import getpass

PASSWORD = "1234"  # 🔐 ตั้งรหัสตรงนี้

# 📌 ฟังก์ชันตรวจสิทธิ์ Admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 📌 ขอสิทธิ์ Admin อัตโนมัติถ้าไม่ได้รันเป็น Admin
def run_as_admin():
    script = sys.executable
    params = " ".join([script] + sys.argv)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", script, " ".join(sys.argv), None, 1)

# 📌 ล็อกและซ่อนโฟลเดอร์
def hide_with_acl(path):
    ctypes.windll.kernel32.SetFileAttributesW(path, 0x02)  # Hidden
    subprocess.run(['icacls', path, '/deny', 'Everyone:(OI)(CI)F'], shell=True)
    print(f"✅ ล็อกและซ่อนโฟลเดอร์: {path}")

# 📌 ปลดล็อกและแสดงโฟลเดอร์
def unhide_with_acl(path):
    subprocess.run(['icacls', path, '/remove:d', 'Everyone'], shell=True)
    ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)  # Normal
    print(f"✅ ปลดล็อกและแสดงโฟลเดอร์: {path}")

# 📌 ขอรหัสผ่าน
def ask_password():
    for _ in range(3):
        input_password = getpass.getpass("🔐 กรุณาใส่รหัสผ่าน: ")
        if input_password == PASSWORD:
            return True
        else:
            print("❌ รหัสผ่านไม่ถูกต้อง!")
    return False

# 📌 โปรแกรมหลัก
def main():
    if not is_admin():
        print("⚠️ ต้องใช้สิทธิ์ Administrator")
        run_as_admin()
        return

    if not ask_password():
        print("❌ ปิดโปรแกรม")
        return

    print("\n📌 คำสั่งใช้งาน:")
    print("  l <พาธโฟลเดอร์>  - ล็อกโฟลเดอร์")
    print("  u <พาธโฟลเดอร์>  - ปลดล็อกโฟลเดอร์")
    print("  exit               - ออกจากโปรแกรม\n")

    while True:
        command = input("คำสั่ง > ").strip()
        if not command:
            continue
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "exit":
            print("👋 ขอบคุณที่ใช้โปรแกรม!")
            break

        if len(parts) != 2:
            print("❌ รูปแบบไม่ถูกต้อง เช่น: l D:\\Folder หรือ u D:\\Folder")
            continue

        folder_path = parts[1]

        if not os.path.exists(folder_path):
            print("❌ ไม่พบโฟลเดอร์นี้")
            continue

        if cmd == "l":
            hide_with_acl(folder_path)
        elif cmd == "u":
            unhide_with_acl(folder_path)
        else:
            print("❌ คำสั่งไม่ถูกต้อง (ใช้ l, u หรือ exit เท่านั้น)")

if __name__ == "__main__":
    main()
