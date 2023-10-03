from flask_smorest import Blueprint
from resources.utils import generate_unique_filename, get_file_extension, transcribe_audio
from flask import current_app, jsonify, request, send_from_directory
from flask.views import MethodView
import os
from werkzeug.utils import secure_filename
import tempfile
from moviepy.editor import VideoFileClip


blp = Blueprint("videos", __name__)


unique_name = generate_unique_filename()


@blp.route("/videos")
class VideoList(MethodView):
    """
    Retrieves a list of video metadata (filename, file size, resolution, and extension) for uploaded videos.
    """

    def get(self):
        try:
            video_folder = current_app.config["UPLOAD_FOLDER"]
            video_files = os.listdir(video_folder)
            video_list = []

            for filename in video_files:
                if filename.endswith((".mp4", ".webm", ".mov")):
                    file_path = os.path.join(video_folder, filename)
                    video_clip = VideoFileClip(file_path)

                    video_info = {
                        "file_name": filename,
                        "file_size": f"{round(os.path.getsize(file_path) / (1024 * 1024), 2)} mb",
                        "resolution": f"{video_clip.size[0]} x {video_clip.size[1]}",
                        "extension": os.path.splitext(filename)[1][1:],
                    }

                    video_list.append(video_info)

            return jsonify(video_list), 200
        except Exception as e:
            return jsonify({"error": str(e)})


@blp.route("/videos/upload", methods=["POST"])
class VideoToDisk(MethodView):
    """
    Uploads and appends video chunks to an existing video file on the disk.
    """

    def post(self):
        content_type = request.headers.get("Content-Type")
        extension = get_file_extension(content_type)
        if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
            os.makedirs(current_app.config["UPLOAD_FOLDER"])
        try:
            video_data = request.data
            if not video_data:
                return jsonify({"error": "Missing video data"}), 400
            if not extension:
                return jsonify({"error": "Unsupported Content-Type"}), 400
            filename = secure_filename(request.headers.get(
                "X-File-Name", f"{unique_name}.{extension}"))
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(file_path):
                with open(file_path, "ab") as f:
                    chunk_size = 10 * 1024 * 1024
                    while True:
                        chunk = request.stream.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
            else:
                with open(file_path, "wb") as f:
                    f.write(video_data)
            return jsonify({"message": "Uploaded successfully", "filename": filename}), 201
        except Exception as e:
            return jsonify({"error": str(e)})


@blp.route("/videos/<filename>")
class VideoPlayBack(MethodView):
    """
    Retrieves and serves the requested video for playback.
    """

    def get(self, filename):
        try:
            return send_from_directory(os.path.join(os.getcwd(), current_app.config["UPLOAD_FOLDER"]), filename)
        except Exception as e:
            return jsonify({"error": str(e)})


@blp.route("/videos/<filename>/transcribe")
class TranscribeVideo(MethodView):
    """
    Transcribes saved video with timestamps.
    """

    def get(self, filename):
        try:
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename)
            if not os.path.exists(file_path):
                return jsonify({"error": "Video not found"}), 404
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
                with open(file_path, "rb") as original_file:
                    temp_video_file.write(original_file.read())
                temp_video_file.seek(0)
                video_clip = VideoFileClip(temp_video_file.name)
                audio_clip = video_clip.audio
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
                    audio_clip.write_audiofile(temp_audio_file.name)
                transcribed_text = transcribe_audio(temp_audio_file.name)
                timestamps = []
                interval = 30  # seconds
                duration = int(video_clip.duration)
                for time in range(0, duration, interval):
                    minutes = time // 60
                    seconds = time % 60
                    timestamp = f"{minutes:02}:{seconds:02}"
                    timestamps.append(timestamp)
                transcribed_with_timestamps = []
                for timestamp, text in zip(timestamps, transcribed_text.splitlines()):
                    transcribed_with_timestamps.append(f"{timestamp} - {text}")
                temp_video_file.close()
                temp_audio_file.close()
                os.remove(temp_video_file.name)
                os.remove(temp_audio_file.name)
            return jsonify({"Transcription": "\n".join(transcribed_with_timestamps)})
        except Exception as e:
            return jsonify({"error": str(e)})
