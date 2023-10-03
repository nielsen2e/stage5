from datetime import datetime
from uuid import uuid4
import whisper


def generate_unique_filename():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid4().hex[:6])
    filename = f"{timestamp}_{unique_id}"
    return filename


def get_file_extension(content_type):
    content_type_map = {
        "video/mp4": "mp4",
        "video/mov": "mov",
        "video/webm": "webm",
    }
    return content_type_map.get(content_type)


def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return str(e)
