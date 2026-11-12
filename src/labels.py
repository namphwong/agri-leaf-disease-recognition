"""Checkpoint output order. Never sort these labels by their display names."""

CLASSES = (
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
)

DISEASE_INFO = {
    "Potato___Early_blight": "A fungal disease that causes dark brown spots on potato leaves and can reduce crop yield.",
    "Potato___Late_blight": "A severe disease that spreads quickly in wet conditions and is responsible for major potato crop losses.",
    "Potato___healthy": "The potato leaf appears healthy with no visible disease symptoms.",
    "Tomato___Early_blight": "A fungal disease that causes brown spots and yellowing on tomato leaves.",
    "Tomato___Late_blight": "A fast-spreading disease that affects tomato plants, especially in humid conditions.",
    "Tomato___healthy": "The tomato leaf appears healthy with no visible disease symptoms.",
}


def pretty_label(label: str) -> str:
    return label.replace("___", " - ").replace("_", " ")


CROP_NAMES = {"Potato": "Khoai tây", "Tomato": "Cà chua"}
CONDITION_NAMES = {"Early_blight": "Early blight", "Late_blight": "Late blight", "healthy": "Lá khỏe"}


def vietnamese_label(label: str) -> str:
    crop, condition = label.split("___")
    return f"{CROP_NAMES[crop]} · {CONDITION_NAMES[condition]}"


DISEASE_INFO_VI = {
    "Early_blight": "Mô hình nhận thấy đặc điểm gần với nhóm Early blight trong dữ liệu học. Cần quan sát thêm điều kiện cây và kiểm chứng chuyên môn trước khi đưa ra kết luận.",
    "Late_blight": "Mô hình nhận thấy đặc điểm gần với nhóm Late blight trong dữ liệu học. Ảnh đơn lẻ chưa đủ để kết luận nguyên nhân hoặc đưa ra cách xử lý.",
    "healthy": "Ảnh gần với nhóm lá khỏe trong dữ liệu học. Kết quả này không loại trừ mọi bệnh hoặc vấn đề khác của cây.",
}
