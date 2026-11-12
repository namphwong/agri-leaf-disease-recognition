import streamlit as st

from src.labels import CLASSES, vietnamese_label
from src.ui.common import header


def render():
    header("HƯỚNG DẪN • NGUỒN", "Một ảnh tốt, một kết quả dễ hiểu", "Ứng dụng minh họa nhận dạng mẫu trong nông nghiệp, dành cho học tập và trình diễn.")
    a, b = st.columns(2, gap="large")
    with a, st.container(border=True):
        st.subheader("Chụp ảnh như thế nào?")
        st.markdown("1. Chọn một lá khoai tây hoặc cà chua.\n2. Chụp cận, đủ sáng, giữ ảnh sắc nét.\n3. Ưu tiên nền đơn giản, không che mặt lá.\n4. Tải JPG/PNG tối đa 20 MiB và 16 triệu pixel.\n5. Bấm phân tích, đọc top 3 và giới hạn trước khi lưu.")
    with b, st.container(border=True):
        st.subheader("Nhận dạng được những gì?")
        for label in CLASSES:
            st.write("• " + vietnamese_label(label))
        st.caption("Giữ tên bệnh Early blight / Late blight theo nhãn dữ liệu để tránh nhầm thuật ngữ.")
    st.subheader("Đọc điểm tin cậy đúng cách")
    st.write("Điểm tin cậy là điểm softmax trong sáu lựa chọn đã học. Điểm cao không bảo đảm đúng; mô hình vẫn chọn một nhãn khi gặp ảnh lạ. Cảnh báo dưới 60% chỉ là gợi ý chụp lại, chưa được hiệu chuẩn thành bộ phát hiện ảnh ngoài phạm vi.")
    st.subheader("Ảnh và lịch sử được giữ ở đâu?")
    st.write("Phân tích chạy trên CPU của máy đang phục vụ ứng dụng. Chỉ khi bấm Lưu kết quả, ứng dụng mới lưu thông tin dự đoán và ảnh xem trước nhỏ vào lịch sử cục bộ. Các phiên trên cùng máy dùng chung lịch sử; bạn có thể xuất CSV hoặc xóa tại mục Lịch sử. Ảnh gốc không được lưu vào lịch sử.")
    st.subheader("Nguồn và đóng góp")
    st.markdown("Mô hình và notebook kế thừa từ [Smart Leaf AI — Supanut Eiamoon](https://github.com/spneoarm/smart-leaf-ai), mã nguồn MIT. Ảnh và metadata từ [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset), dataset card công bố [CC BY-SA 3.0](https://huggingface.co/datasets/mohanty/PlantVillage). Ảnh mẫu được lấy từ phần train của split dự án; khi chưa có dữ liệu trên máy, chỉ ảnh mẫu bạn chọn được tải từ GitHub public và kiểm tra checksum.")
    st.write("namphwong phát triển cấu trúc dịch vụ, kiểm chứng pipeline, chuẩn bị dữ liệu, UI/UX tiếng Việt, lịch sử SQLite và xuất CSV. Không coi mô hình kế thừa là thuật toán tự xây dựng.")
    st.link_button("Xem mã nguồn dự án", "https://github.com/namphwong/agri-leaf-disease-recognition")
    st.info("Kết quả phục vụ học tập, không dùng làm kết luận chẩn đoán hoặc hướng dẫn thuốc và canh tác.")
