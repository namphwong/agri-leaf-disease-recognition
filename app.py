import streamlit as st

from src.storage import HistoryStore
from src.ui import evaluation, guide, history, recognition
from src.ui.common import theme

st.set_page_config(page_title="Agri Leaf · Nhận dạng bệnh lá", page_icon="🌿", layout="wide", initial_sidebar_state="auto")
theme()

with st.sidebar:
    st.markdown('<div class="leaf-brand">🌿 Agri Leaf</div>', unsafe_allow_html=True)
    st.caption("NHẬN DẠNG MẪU TRONG NÔNG NGHIỆP")
    st.divider()
    page = st.radio("Không gian làm việc", ["Nhận dạng", "Lịch sử", "Đánh giá", "Hướng dẫn"], key="navigation")
    st.divider()
    st.markdown("**Hai loại cây. Sáu nhóm lá.**")
    st.caption("Khoai tây & cà chua\n\nResNet18 · xử lý trên CPU")
    st.caption("Dự án học phần của namphwong. Kết quả dùng để học tập và minh họa.")

store = HistoryStore()
if page == "Nhận dạng":
    recognition.render(store)
elif page == "Lịch sử":
    history.render(store)
elif page == "Đánh giá":
    evaluation.render()
else:
    guide.render()

st.divider()
st.caption("Agri Leaf · Nhận dạng từ ảnh, diễn giải có giới hạn. Nguồn: Smart Leaf AI & PlantVillage.")
