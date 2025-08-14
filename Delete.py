import os
import shutil
import hashlib
import datetime
import getpass
import sys

# ==== สถานะภายใน ====
_protected_paths = []          # รายการ path ที่บล็อกไม่ให้ลบ
_password_hash = None          # เก็บ hash ของรหัสผ่าน
_cooldown_until = None         # เวลาเลิกคูลดาวน์ (datetime) ถ้าใส่รหัสผิด

# ==== ยูทิลิตี้เส้นทาง ====
def normalize_path(path: str) -> str:
    return os.path.abspath(os.path.normpath(path))

def get_self_path() -> str:
    """คืน path ของไฟล์ .exe (เมื่อแพ็กด้วย PyInstaller) หรือ .py ที่กำลังรันอยู่"""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys.executable)
    # กรณีรันเป็นสคริปต์
    return os.path.abspath(__file__)

def protect_path(path: str):
    """เพิ่ม path ที่ต้องการบล็อกไม่ให้ลบ (ครอบคลุมทั้งไฟล์และโฟลเดอร์ย่อย)"""
    full_path = normalize_path(path)
    if full_path not in _protected_paths:
        _protected_paths.append(full_path)
        print(f"✅ บล็อกไม่ให้ลบ: {full_path}")

def is_protected(path: str) -> bool:
    """เช็กว่า path นี้โดนบล็อกไหม (รวมถึงไฟล์ .exe/.py ตัวเอง)"""
    path = normalize_path(path)

    # 1) กันลบไฟล์ที่กำลังรันอยู่ (.exe เมื่อแพ็ก, หรือ .py ตอนพัฒนา)
    self_path = get_self_path()
    if path == normalize_path(self_path):
        return True

    # 2) กันลบทุกอย่างที่อยู่ใต้รายการที่บล็อกไว้
    for protected in _protected_paths:
        protected = normalize_path(protected)
        if path == protected or path.startswith(protected + os.sep):
            return True
    return False

def protect_self(protect_parent: bool = True):
    """บล็อกไฟล์ตัวเอง และ (ตัวเลือก) โฟลเดอร์ที่เก็บตัวเองเพื่อกัน rmdir"""
    self_path = get_self_path()
    protect_path(self_path)
    if protect_parent:
        parent = os.path.dirname(self_path)
        protect_path(parent)

# ==== ระบบรหัสผ่าน + คูลดาวน์ ====
def set_password(password: str):
    """ตั้งรหัสผ่าน (เก็บเป็น SHA-256 hash ในหน่วยความจำเท่านั้น)"""
    global _password_hash
    _password_hash = hashlib.sha256(password.encode()).hexdigest()

def _is_in_cooldown() -> bool:
    if _cooldown_until is None:
        return False
    return datetime.datetime.now() < _cooldown_until

def _check_password(input_password: str) -> bool:
    """ตรวจรหัสผ่าน: ถ้าผิด → คูลดาวน์ 1 ชั่วโมง"""
    global _cooldown_until
    if _is_in_cooldown():
        raise PermissionError("⏳ ใส่รหัสผิดก่อนหน้านี้ ต้องรอ 1 ชั่วโมงก่อนลองใหม่")

    if _password_hash is None:
        raise ValueError("ยังไม่ได้ตั้งรหัสผ่าน")

    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    if input_hash == _password_hash:
        return True

    _cooldown_until = datetime.datetime.now() + datetime.timedelta(hours=1)
    raise PermissionError("❌ รหัสผ่านไม่ถูกต้อง! ระบบล็อกไว้ 1 ชั่วโมง")

def prompt_login() -> bool:
    """ขอรหัสผ่านตอนเปิดโปรแกรมก่อนเข้าโหมดควบคุม"""
    if _password_hash is None:
        raise ValueError("ยังไม่ได้ตั้งรหัสผ่าน")

    print("🔐 เข้าสู่ระบบ: ใส่รหัสผ่านเพื่อเริ่มควบคุม")
    try:
        password = getpass.getpass("🔒 ใส่รหัสผ่าน: ")
        _check_password(password)
        print("✅ เข้าสู่ระบบสำเร็จ\n")
        return True
    except PermissionError as e:
        print(e)
        return False

def _ask_password_and_validate():
    """ขอรหัสผ่านก่อน ‘ลบของที่ถูกบล็อก’ (ใช้กับ safe_remove/rmdir/rmtree)"""
    if _password_hash is None:
        raise ValueError("ยังไม่ได้ตั้งรหัสผ่าน")
    password = getpass.getpass("🔒 ยืนยันรหัสผ่านก่อนลบ: ")
    _check_password(password)

# ==== ฟังก์ชันลบแบบปลอดภัย ====
def safe_remove(path: str):
    """แทน os.remove: ลบไฟล์ แต่ถ้าอยู่ในเขตบล็อก → ขอรหัสผ่าน/บล็อก"""
    if is_protected(path):
        _ask_password_and_validate()
    os.remove(path)

def safe_rmdir(path: str):
    """แทน os.rmdir: ลบโฟลเดอร์ว่าง แต่ถ้าอยู่ในเขตบล็อก → ขอรหัสผ่าน/บล็อก"""
    if is_protected(path):
        _ask_password_and_validate()
    os.rmdir(path)

def safe_rmtree(path: str):
    """แทน shutil.rmtree: ลบทั้งโฟลเดอร์ แต่ถ้าอยู่ในเขตบล็อก → ขอรหัสผ่าน/บล็อก"""
    if is_protected(path):
        _ask_password_and_validate()
    shutil.rmtree(path)
