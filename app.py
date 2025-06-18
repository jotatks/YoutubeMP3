from flask import Flask, render_template, request, send_from_directory
import os
from yt_dlp import YoutubeDL
from uuid import uuid4

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not url:
            return render_template('index.html', error="URL vazia.")

        output_id = str(uuid4())  # cria nome único para evitar conflito
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{output_id}.mp3")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': False,  # suporta playlists!
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            return render_template('index.html', error=str(e))

        filename = os.path.basename(output_path)
        return render_template('index.html', success=True, filename=filename)

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
