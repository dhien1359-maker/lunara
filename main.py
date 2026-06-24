"""
●'◡'● Lunara Desktop Pet
Chạy: python main.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.pet import CirclePet

if __name__ == "__main__":
    print("🌸 Lunara đang khởi động...")
    print("  Bôi đen + Ctrl+C → dịch tự động")
    print("  Double-click → đổi mood")
    print("  Kéo nhanh + thả → ném")
    print("  Chuột phải → menu")
    CirclePet().run()
