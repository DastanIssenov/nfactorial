from flask import Flask, request, jsonify
from flask_cors import CORS
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
AUDIO_FOLDER = "static/audio"

# keep downloaded album entry
downloaded_album = {
    "id": 999,
    "title": "YouTube Downloads",
    "artist": "Various",
    "cover": "https://via.placeholder.com/50x50?text=YT",
    "trackIds": []
}

@app.route("/download", methods=["POST"])
def download_audio():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify(success=False, error="No URL")

    print("📥 Получен запрос на скачивание")

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print("▶ yt.title:", yt.title)

        audio = yt.streams.filter(only_audio=True).first()
        if not audio:
            raise Exception("No audio stream found")

        filename = secure_filename(f"{yt.title}_audio.mp4")
        path = os.path.join(AUDIO_FOLDER, filename)
        audio.download(output_path=AUDIO_FOLDER, filename=filename)

        video_id = yt.video_id
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
        track_id = hash(video_id) % 1000000000

        track = {
            "id": track_id,
            "title": yt.title,
            "artist": yt.author,
            "genre": "YouTube",
            "cover": thumbnail_url,
            "albumId": downloaded_album["id"],
            "src": f"/static/audio/{filename}"
        }

        # append track to the downloaded album
        downloaded_album["trackIds"].append(track_id)

        return jsonify(success=True, track=track, album=downloaded_album)

    except Exception as e:
        print("❌ Ошибка при загрузке:", e)
        return jsonify(success=False, error=str(e))

if __name__ == "__main__":
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    app.run(debug=True)
