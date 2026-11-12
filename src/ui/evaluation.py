import json

import streamlit as st

from src.config import PROJECT_ROOT
from src.labels import vietnamese_label
from src.ui.common import header


def render():
    header("MINH CHỨNG • PHẠM VI", "Hiểu kết quả trước khi tin dùng", "Các số liệu dưới đây lấy từ báo cáo đã chạy của dự án; không thay thế kiểm chứng ngoài thực tế.")
    try:
        dataset = json.loads((PROJECT_ROOT / "reports/dataset/summary.json").read_text(encoding="utf-8"))
        baseline = json.loads((PROJECT_ROOT / "reports/baseline/phase4-results.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st.error("Chưa đọc được báo cáo đánh giá. Vui lòng thử lại sau.")
        return
    a, b, c = st.columns(3)
    a.metric("Ảnh đã kiểm tra dữ liệu", f'{dataset["images"]:,}'.replace(",", "."))
    b.metric("Nhóm nhận dạng", "6")
    c.metric("Ảnh kiểm chứng kỹ thuật", f'{baseline["sample_matches"]}/{baseline["sample_count"]} khớp nhãn')
    st.info("6/6 ảnh là kiểm tra kỹ thuật, không phải độ chính xác 100% trên tập test độc lập. Các ảnh có thể đã xuất hiện trong huấn luyện mô hình kế thừa.")
    with st.container(border=True):
        st.subheader("Dữ liệu có gì?")
        maximum = max(row["images"] for row in dataset["per_class"])
        for row in dataset["per_class"]:
            name, bar = st.columns([1.1, 2])
            name.caption(vietnamese_label(row["label"]))
            bar.progress(row["images"] / maximum, text=f'{row["images"]:,} ảnh'.replace(",", "."))
        st.caption(f'{dataset["quarantined_images"]:,} ảnh thiếu thông tin nhóm lá được giữ riêng; {dataset["selected_images"]:,} ảnh đủ điều kiện tạo split mới.'.replace(",", "."))
        table = "| Nhóm | Train | Validation | Test | Giữ riêng |\n|---|---:|---:|---:|---:|\n"
        table += "\n".join(f'| {vietnamese_label(row["label"])} | {row["train"]} | {row["validation"]} | {row["test"]} | {row["quarantine"]} |' for row in dataset["per_class"])
        st.markdown(table)
    left, right = st.columns(2, gap="large")
    with left, st.container(border=True):
        st.subheader("Đã kiểm chứng")
        st.write("✓ Mô hình chạy trên CPU\n\n✓ Sáu ảnh cho kết quả khớp trước và sau tách mã\n\n✓ Pipeline giữ nguyên thứ tự nhãn và tiền xử lý")
        st.caption("Nguồn: báo cáo baseline và hồi quy Phase 4. Thời gian đo không gồm toàn bộ thao tác giao diện.")
    with right, st.container(border=True):
        st.subheader("Chưa thể kết luận")
        st.write("Khả năng nhận dạng ảnh ngoài đồng, cây ngoài phạm vi và chất lượng trên một tập test độc lập của mô hình kế thừa chưa được xác nhận.")
        st.caption("Accuracy, precision, recall, F1 và confusion matrix đầy đủ sẽ được công bố sau bước thực nghiệm Phase 6, với điều kiện đánh giá rõ ràng.")
    st.link_button("Đọc phương pháp đánh giá", "https://github.com/namphwong/agri-leaf-disease-recognition/blob/main/docs/dataset.md")
