"""Decode uploads without relying on the filename or writing user files."""

import io

from PIL import Image, UnidentifiedImageError

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000


class ImageValidationError(ValueError):
    """An upload cannot be accepted as a supported image."""


def decode_image(payload: bytes) -> Image.Image:
    if not payload:
        raise ImageValidationError("The image file is empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise ImageValidationError("The image file must not exceed 20 MiB.")
    try:
        with Image.open(io.BytesIO(payload)) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ImageValidationError("Only JPEG and PNG image content is supported.")
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ImageValidationError("The image must not exceed 16 million pixels.")
            image.verify()
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            return image.convert("RGB")
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ImageValidationError("The image file is invalid or cannot be decoded.") from exc
