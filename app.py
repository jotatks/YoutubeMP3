from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'URL não fornecida'})

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            files = []
            if 'entries' in info:  # playlist
                for entry in info['entries']:
                    if entry is None:
                        continue
                    title = entry.get('title')
                    filename = f"{title}.mp3"
                    files.append(filename)
            else:
                title = info.get('title')
                filename = f"{title}.mp3"
                files.append(filename)

            file_urls = [f"/download/{file}" for file in files]

            return jsonify({'success': True, 'files': file_urls, 'filenames': files})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    return render_template('index.html')


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
