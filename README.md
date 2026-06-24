# 🌸 Lunara Desktop Pet

## Cài đặt
pip install -r requirements.txt

## Cấu hình API key
Mở `features/translate.py`, thay dòng:
ANTHROPIC_API_KEY = "YOUR_API_KEY_HERE"

## Chạy
python main.py

## Cấu trúc
lunara/
├── main.py                  ← Entry point, chạy cái này
├── requirements.txt
├── core/
│   ├── pet.py               ← Vòng lặp chính
│   ├── physics.py           ← Vật lý: gravity, bounce, ném
│   └── renderer.py          ← Vẽ nhân vật
└── features/
    ├── mood.py              ← Mood & màu sắc
    └── translate.py         ← Dịch thuật (API key ở đây)

## Chức năng
1. đổi màu
2. dịch thuật
3. ném
4. tự di chuyển
5. ăn file rác
6. biến đổi biểu
7. hẹn giờ, cảnh báo
8. lên lịch

## Tính năng Lịch & Hẹn giờ
Chuột phải → 📅 Lịch & Hẹn giờ

- **Đồng hồ**: hiện giờ + ngày thứ realtime
- **Nhắc lịch**: đặt ngày giờ cụ thể, có preset nhanh (5/15/30 phút, 1 giờ)
- **Đếm ngược**: hẹn giờ đếm ngược H:M:S, cảnh báo khi hết
- **Danh sách**: xem & xoá các nhắc lịch sắp tới
- **Lưu tự động**: lịch được lưu vào data/reminders.json
