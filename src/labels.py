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
