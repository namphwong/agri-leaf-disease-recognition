import json

import streamlit as st

from src.config import PROJECT_ROOT
from src.evaluation import EVALUATION_PATH, load_evaluation
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
    try:
        report = load_evaluation()
    except (OSError, ValueError, KeyError):
        st.error("Chưa xác minh được báo cáo đánh giá mô hình. Các chỉ số chưa được hiển thị để tránh dùng số liệu không khớp.")
    else:
        st.subheader("Kiểm chứng checkpoint · 776 ảnh")
        st.warning(report["warning_vi"])
        metrics = report["metrics"]
        columns = st.columns(4)
        for column, title, key in zip(columns, ("Accuracy (kiểm chứng)", "Precision macro", "Recall macro", "F1 macro"),
                                      ("accuracy", "macro_precision", "macro_recall", "macro_f1")):
            column.metric(title, f'{metrics[key] * 100:.2f}%')
        interval = report["bootstrap"]["accuracy_95_interval"]
        st.caption(f'{metrics["sample_count"]} ảnh · {report["groups"]} nhóm lá · Khoảng bootstrap 95% theo nhóm cho accuracy: {interval[0]:.2%}–{interval[1]:.2%}. Khoảng này không khắc phục nguy cơ trùng dữ liệu huấn luyện.')
        scores_tab, matrix_tab, examples_tab = st.tabs(["Từng lớp", "Ma trận nhầm lẫn", "Ví dụ & thời gian"])
        with scores_tab:
            table = "| Nhóm | Precision | Recall | F1 | Số ảnh |\n|---|---:|---:|---:|---:|\n"
            table += "\n".join(f'| {vietnamese_label(row["label"])} | {row["precision"]:.2%} | {row["recall"]:.2%} | {row["f1"]:.2%} | {row["support"]} |' for row in metrics["per_class"])
            st.markdown(table)
            st.caption("Potato healthy chỉ có 7 nhóm lá trong phần kiểm chứng; kết quả lớp ít mẫu có độ bất định lớn.")
        with matrix_tab:
            st.image(str(EVALUATION_PATH / "confusion_matrix.png"), width="stretch")
            st.caption("Hàng: nhãn dữ liệu. Cột: dự đoán. Mỗi ô có số ảnh và tỷ lệ theo hàng.")
        with examples_tab:
            st.write(f'Trung vị decode + tiền xử lý + suy luận: **{report["timing"]["median_decode_predict_ms"]:.2f} ms/ảnh**; p95 **{report["timing"]["p95_decode_predict_ms"]:.2f} ms/ảnh** trên CPU đã kiểm chứng. Không gồm đọc file, checksum hoặc toàn bộ thao tác giao diện.')
            st.image(str(EVALUATION_PATH / "latency.png"), width="stretch")
            st.image(str(EVALUATION_PATH / "examples.png"), width="stretch")
            st.caption("Ảnh PlantVillage, CC BY-SA 3.0 theo dataset card. Ví dụ chọn sau khi đánh giá để phân tích lỗi; không điều chỉnh mô hình từ các ảnh này.")
        st.download_button("Tải báo cáo chỉ số JSON", (EVALUATION_PATH / "latest.json").read_bytes(),
                           file_name="danh-gia-checkpoint.json", mime="application/json", key="download_evaluation")
        st.caption(f'Checkpoint {report["model_version"]} · báo cáo {report["created_at"][:10]} · dữ liệu và dự đoán đã kiểm tra checksum.')
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
        st.caption("Các chỉ số checkpoint phía trên vẫn là kiểm chứng có nguy cơ trùng huấn luyện. Muốn có đánh giá độc lập cần huấn luyện lại theo split đã cố định và giữ test để đánh giá cuối.")
    st.link_button("Đọc phương pháp đánh giá", "https://github.com/namphwong/agri-leaf-disease-recognition/blob/main/docs/dataset.md")
