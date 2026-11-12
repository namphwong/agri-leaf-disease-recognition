import hashlib
import logging

import streamlit as st

from src.config import DEFAULT_MODEL_PATH
from src.inference import load_model, predict
from src.labels import CROP_NAMES, DISEASE_INFO_VI, vietnamese_label
from src.samples import sample_bytes, sample_manifest
from src.storage import HistoryError, make_history_record
from src.ui.common import header, thumbnail, top_predictions
from src.validation import ImageValidationError, decode_image

logger = logging.getLogger(__name__)


@st.cache_resource
def cached_model(path, modified_ns, size):
    return load_model(path)


@st.cache_data(show_spinner=False)
def cached_sample(index):
    return sample_bytes(index)


def set_image(payload, name):
    st.session_state.active_image = {"bytes": payload, "name": name}
    st.session_state.pop("analysis", None)
    st.session_state.pop("saved_record", None)


def render(store):
    header("NHẬN DẠNG • ẢNH LÁ", "Mỗi chiếc lá, một góc nhìn.",
           "Tải ảnh lá khoai tây hoặc cà chua để khám phá kết quả từ mô hình nhận dạng.")
    upload_col, sample_col = st.columns([1.4, 1], gap="large")
    with upload_col, st.container(border=True):
        st.subheader("01 · Chọn ảnh của bạn")
        st.caption("Một lá rõ nét, đủ sáng và có nền đơn giản.")
        uploaded = st.file_uploader("Tải ảnh lá cây", type=["jpg", "jpeg", "png"],
                                    key=f'upload_{st.session_state.get("upload_revision", 0)}',
                                    help="JPEG/PNG · tối đa 20 MiB · tối đa 16 triệu pixel.")
        if uploaded is not None:
            payload = uploaded.getvalue()
            fingerprint = hashlib.sha256(payload).hexdigest()
            if fingerprint != st.session_state.get("last_uploaded_digest"):
                set_image(payload, getattr(uploaded, "name", "anh-tai-len.png"))
                st.session_state.last_uploaded_digest = fingerprint
    with sample_col, st.container(border=True):
        st.subheader("Hoặc thử một ảnh mẫu")
        st.caption("Ảnh PlantVillage, đã chọn từ phần dữ liệu train.")
        samples = sample_manifest()
        index = st.selectbox("Loại ảnh mẫu", range(len(samples)),
                             format_func=lambda i: vietnamese_label(samples[i]["label"]), key="sample_choice")
        if st.button("Dùng ảnh mẫu", key="use_sample", width="stretch"):
            try:
                with st.spinner("Đang chuẩn bị ảnh mẫu…"):
                    set_image(cached_sample(index), samples[index]["source_path"].rsplit("/", 1)[-1])
            except Exception:
                logger.exception("Sample could not be loaded")
                st.error("Không tải được ảnh mẫu. Hãy thử lại hoặc chọn ảnh từ máy.")

    active = st.session_state.get("active_image")
    if not active:
        with st.container(border=True):
            st.subheader("Bắt đầu từ một chiếc lá")
            st.write("Chọn ảnh từ máy hoặc dùng ảnh mẫu ở trên. Bạn sẽ xem được loại cây, nhóm bệnh và ba dự đoán cao nhất.")
            a, b, c = st.columns(3)
            a.markdown("**1. Chọn ảnh**\n\nChụp cận một lá, tránh bóng tối.")
            b.markdown("**2. Phân tích**\n\nMô hình so sánh với sáu nhóm đã học.")
            c.markdown("**3. Xem & lưu**\n\nĐọc kết quả, lưu khi bạn cần.")
        st.caption("Phạm vi: khoai tây và cà chua · Early blight, Late blight, lá khỏe.")
        return

    if st.button("Chọn ảnh khác", key="reset_image"):
        for key in ("active_image", "analysis", "saved_record", "last_uploaded_digest"):
            st.session_state.pop(key, None)
        st.session_state.upload_revision = st.session_state.get("upload_revision", 0) + 1
        st.rerun()
    try:
        image = decode_image(active["bytes"])
    except ImageValidationError as exc:
        st.error(str(exc))
        return

    preview_col, result_col = st.columns([1.05, 1], gap="large")
    with preview_col, st.container(border=True):
        st.subheader("02 · Xem trước ảnh")
        preview = image.copy()
        preview.thumbnail((700, 420))
        st.image(preview, width="stretch")
        st.text(active["name"])
        st.caption(f"{image.width} × {image.height} px · JPEG/PNG · xử lý trên CPU")
        if st.button("Phân tích ảnh", type="primary", key="analyze", width="stretch"):
            st.session_state.pop("analysis", None)
            st.session_state.pop("saved_record", None)
            try:
                with st.spinner("Đang đọc đặc điểm của lá…"):
                    stat = DEFAULT_MODEL_PATH.stat()
                    model = cached_model(str(DEFAULT_MODEL_PATH), stat.st_mtime_ns, stat.st_size)
                    st.session_state.analysis = predict(model, image)
            except Exception:
                logger.exception("Model prediction failed")
                st.error("Chưa thể phân tích ảnh. Hãy kiểm tra mô hình và thử lại.")

    with result_col, st.container(border=True):
        st.subheader("03 · Kết quả nhận dạng")
        result = st.session_state.get("analysis")
        if result is None:
            st.info("Ảnh đã sẵn sàng. Bấm “Phân tích ảnh” để xem kết quả.")
            st.caption("Mô hình chỉ nhận dạng sáu nhóm đã học; không xác nhận được mọi loại cây hoặc bệnh.")
            return
        crop, condition = result.label.split("___")
        st.caption(CROP_NAMES[crop].upper())
        st.subheader(vietnamese_label(result.label))
        st.metric("Điểm tin cậy", f"{result.confidence * 100:.2f}%",
                  help="Điểm softmax của mô hình, không phải xác suất chẩn đoán đúng đã được hiệu chuẩn.")
        if result.confidence < 0.60:
            st.warning("Điểm dự đoán thấp. Hãy thử ảnh rõ hơn và đọc thêm các khả năng bên dưới.")
        st.write(DISEASE_INFO_VI[condition])
        st.divider()
        st.markdown("**Ba khả năng cao nhất**")
        top_predictions(result.top3)
        st.caption("Điểm cao vẫn có thể sai, nhất là với ảnh ngoài đồng hoặc cây không được hỗ trợ.")
        if st.button("Lưu kết quả", key="save_result", width="stretch"):
            try:
                identifier, created = store.save(make_history_record(result, active["name"], active["bytes"]), thumbnail(image))
                st.session_state.saved_record = identifier
                st.success("Đã lưu vào lịch sử." if created else "Ảnh này đã có trong lịch sử với cùng phiên bản mô hình.")
            except HistoryError as exc:
                logger.exception("History save failed")
                st.error(str(exc))
        st.caption("Chỉ lưu khi bạn bấm nút: thông tin kết quả và ảnh xem trước nhỏ, trên máy chạy ứng dụng.")
        with st.expander("Thông tin lần phân tích"):
            st.text(f"Phiên bản: {result.model_version}")
            st.caption("Nguồn mô hình: Smart Leaf AI · ResNet18 / PlantVillage.")
