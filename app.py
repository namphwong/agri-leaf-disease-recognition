import streamlit as st

from src.config import DEFAULT_MODEL_PATH
from src.inference import load_model, predict
from src.labels import CLASSES, DISEASE_INFO, pretty_label
from src.validation import decode_image

st.set_page_config(page_title="Smart Leaf AI", page_icon="🌿", layout="wide")

st.markdown(
    """
    <style>
    .hero-card {
        padding: 1.4rem 1.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.10);
        margin-bottom: 1rem;
    }
    .small-muted {
        color: #5f6b61;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin:0;">Smart Leaf AI 🌿</h1>
        <p style="margin:0.5rem 0 0 0; font-size:1.05rem;">
            Upload a potato or tomato leaf image to predict whether it is healthy or diseased.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<p class='small-muted'>Built with PyTorch + ResNet18 + Streamlit</p>",
    unsafe_allow_html=True,
)


@st.cache_resource
def cached_model(path: str, modified_ns: int, size: int):
    # File identity participates in Streamlit's cache key.
    return load_model(path)


try:
    model_stat = DEFAULT_MODEL_PATH.stat()
    model = cached_model(str(DEFAULT_MODEL_PATH), model_stat.st_mtime_ns, model_stat.st_size)
except FileNotFoundError:
    st.error(f"Model file not found: {DEFAULT_MODEL_PATH}")
    st.stop()
except Exception as exc:
    st.error(f"Failed to load model: {exc}")
    st.stop()

left_col, right_col = st.columns([1.05, 1], gap="large")

with left_col, st.container(border=True):
    st.subheader("Upload Leaf Image")
    st.write("Choose a clear image of a potato or tomato leaf.")
    uploaded_file = st.file_uploader(
        "Supported formats: JPG, JPEG, PNG",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help="JPEG/PNG, up to 20 MiB and 16 million pixels.",
    )
    st.markdown(
        "<p class='small-muted'>Tip: use a close-up image with good lighting and a visible leaf surface.</p>",
        unsafe_allow_html=True,
    )

with right_col, st.container(border=True):
    st.subheader("Supported Classes")
    st.write("This demo currently predicts these categories:")
    for cls in CLASSES:
        st.write(f"• {pretty_label(cls)}")

if uploaded_file is None:
    st.info("Upload a potato or tomato leaf image to see a prediction.")
else:
    try:
        image = decode_image(uploaded_file.getvalue())

        with st.spinner("Analyzing leaf image with AI..."):
            result = predict(model, image)

        pred_label = result.label
        confidence = result.confidence * 100

        preview_col, result_col = st.columns([1.05, 1], gap="large")

        with preview_col, st.container(border=True):
            st.subheader("Image Preview")
            st.image(image, caption="Uploaded Leaf Image", width="stretch")

        with result_col, st.container(border=True):
            st.subheader("Prediction Result")
            st.metric("Predicted Class", pretty_label(pred_label))
            st.metric("Confidence", f"{confidence:.2f}%")
            st.progress(min(max(int(confidence), 0), 100))

            st.write("### Top Predictions")
            for prediction in result.top3:
                pct = prediction.score * 100
                st.write(f"**{pretty_label(prediction.label)} — {pct:.2f}%**")
                st.progress(min(max(int(pct), 0), 100))

            st.write("### Disease Description")
            st.info(DISEASE_INFO[pred_label])

    except Exception as exc:
        st.error(f"Prediction failed: {exc}")

st.markdown("---")
st.caption("Demo project for plant disease classification using computer vision.")
