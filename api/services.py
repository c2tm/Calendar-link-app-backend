import uuid
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import IcsFile
from .ical_utils import normalize_crlf

def save_ics_and_get_url(ics_text: str, request, suggested_name: str | None = None) -> str:
    text = normalize_crlf(ics_text)
    name = slugify(suggested_name or "event") or "event"
    filename = f"{name}-{uuid.uuid4().hex}.ics"
    obj = IcsFile()
    obj.file.save(filename, ContentFile(text), save=True)
    url = obj.file.url
    return request.build_absolute_uri(url)