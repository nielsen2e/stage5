import os


class Config():
    API_TITLE = "Chrome Extension API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
