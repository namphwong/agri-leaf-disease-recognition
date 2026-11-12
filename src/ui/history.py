import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from src.labels import CLASSES, CROP_NAMES, vietnamese_label
from src.storage import HistoryError, export_csv
from src.ui.common import header, top_predictions


def render(store):
    header("NHẬT KÝ • ĐÃ LƯU", "Lịch sử của những chiếc lá", "Xem lại, lọc và xuất những kết quả bạn đã chủ động lưu.")
    st.caption("Lịch sử dùng chung trên máy chạy ứng dụng; không đồng bộ tài khoản. Ảnh gốc không được lưu.")
    if message := st.session_state.pop("history_notice", None):
        st.success(message)
    search_col, crop_col, label_col = st.columns([1.5, 1, 1.4])
    search = search_col.text_input("Tìm tên ảnh", placeholder="Nhập một phần tên ảnh…", key="history_search")
    crop = crop_col.selectbox("Loại cây", ["", "Potato", "Tomato"],
                              format_func=lambda c: CROP_NAMES.get(c, "Tất cả"), key="history_crop")
    label = label_col.selectbox("Nhóm kết quả", [""] + [c for c in CLASSES if not crop or c.startswith(crop)],
                                format_func=lambda c: vietnamese_label(c) if c else "Tất cả", key="history_label")
    filters = dict(search=search, crop=crop, label=label)
    if st.checkbox("Lọc theo ngày", key="filter_dates"):
        today = datetime.now(ZoneInfo("Asia/Bangkok")).date()
        a, b = st.columns(2)
        start = a.date_input("Từ ngày", today - timedelta(days=30), format="DD/MM/YYYY")
        end = b.date_input("Đến ngày", today, format="DD/MM/YYYY")
        if start > end:
            st.error("Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.")
            return
        filters.update(start_date=start.isoformat(), end_date=end.isoformat())
    try:
        count = store.count(**filters)
        total = store.count()
        left, right = st.columns([2, 1])
        left.caption(f"{count} kết quả phù hợp · {total} kết quả đã lưu")
        st.caption("CSV dùng điểm ở miền 0–1 và gồm phiên bản mô hình để đối chiếu.")
        if count:
            right.download_button("Xuất CSV theo bộ lọc", export_csv(store.list(limit=None, include_thumbnails=False, **filters)),
                                  file_name="lich-su-nhan-dang.csv", mime="text/csv", key="export_history", width="stretch")
        if not count:
            st.info("Chưa có kết quả phù hợp. Hãy đổi bộ lọc hoặc lưu một lần nhận dạng mới.")
        else:
            page = st.selectbox("Trang", range(1, math.ceil(count / 10) + 1), key=f"history_page_{count}")
            for record in store.list(limit=10, offset=(page - 1) * 10, **filters):
                with st.container(border=True):
                    picture_col, text_col = st.columns([1, 4])
                    picture_col.image(record["thumbnail"], width="stretch")
                    with text_col:
                        st.markdown(f'**{vietnamese_label(record["label"])}**')
                        st.text(record["image_name"])
                        st.caption(f'{record["created_at"][:19].replace("T", " ")} · Điểm {record["confidence"] * 100:.2f}%')
                        with st.expander("Chi tiết và thao tác"):
                            top_predictions(record["prediction"]["top3"])
                            st.caption(f'Phiên bản {record["model_version"]} · giờ Việt Nam (UTC+7)')
                            confirmed = st.checkbox("Tôi muốn xóa kết quả này", key=f'confirm_{record["id"]}')
                            if st.button("Xóa kết quả", key=f'delete_{record["id"]}', disabled=not confirmed):
                                store.delete(record["id"])
                                st.session_state.history_notice = "Đã xóa kết quả."
                                st.rerun()
        if total:
            with st.expander("Quản lý toàn bộ lịch sử"):
                st.write(f"Xóa cả {total} kết quả đã lưu, bao gồm các mục ngoài bộ lọc hiện tại.")
                confirmed = st.checkbox("Tôi xác nhận xóa toàn bộ lịch sử", key="confirm_clear")
                if st.button("Xóa toàn bộ lịch sử", key="clear_history", disabled=not confirmed):
                    store.clear()
                    st.session_state.history_notice = "Đã xóa toàn bộ lịch sử."
                    st.rerun()
    except HistoryError as exc:
        st.error(str(exc))
        st.info("Bạn vẫn có thể nhận dạng ảnh; phần lưu lịch sử hiện chưa sẵn sàng.")
