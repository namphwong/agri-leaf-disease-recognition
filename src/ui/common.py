import io

import streamlit as st
from PIL import Image

from src.labels import vietnamese_label


def header(eyebrow, title, description):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(description)


def thumbnail(image: Image.Image) -> bytes:
    preview = image.convert("RGB").copy()
    preview.thumbnail((320, 240))
    output = io.BytesIO()
    preview.save(output, format="JPEG", quality=80)
    return output.getvalue()


def top_predictions(predictions):
    for prediction in predictions:
        label = prediction["label"] if isinstance(prediction, dict) else prediction.label
        score = prediction["score"] if isinstance(prediction, dict) else prediction.score
        name_col, score_col = st.columns([4, 1])
        name_col.write(vietnamese_label(label))
        score_col.write(f"{score * 100:.2f}%")
        st.progress(min(max(float(score), 0), 1))


def theme():
    st.markdown("""<style>
    .block-container {max-width:1200px;padding-top:2.3rem;padding-bottom:3rem;}
    h1 {letter-spacing:-0.045em;font-weight:750!important;font-size:2.7rem!important;line-height:1.15!important;}
    h2,h3 {letter-spacing:-0.025em;}
    .eyebrow {color:#176b4c;font-size:.73rem;font-weight:750;letter-spacing:.15em;margin-bottom:.65rem;}
    [data-testid="stSidebar"] {border-right:1px solid #dfe7dd;}
    [data-testid="stSidebar"] .block-container {padding-top:1.5rem;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px;}
    [data-testid="stFileUploaderDropzone"] {border:1.5px dashed #9ebaa8;border-radius:14px;background:#f9fbf7;}
    .stButton>button,.stDownloadButton>button {border-radius:10px;font-weight:600;min-height:2.65rem;}
    [data-testid="stMetricValue"] {font-size:2rem;letter-spacing:-.04em;}
    [data-testid="stCaptionContainer"] {color:#52665b;}
    [data-testid="stMarkdownContainer"] table {display:block;overflow-x:auto;max-width:100%;}
    .leaf-brand {font-size:1.35rem;font-weight:800;letter-spacing:-.04em;margin-bottom:.2rem;}
    @media(max-width:640px) {
      .block-container {padding-top:1.5rem;padding-left:1rem;padding-right:1rem;}
      h1 {font-size:2.1rem!important;}
    }
    </style>""", unsafe_allow_html=True)
