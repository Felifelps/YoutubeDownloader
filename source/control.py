import os
import platform
import shutil
import subprocess

import imageio_ffmpeg
from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename


def _ffmpeg_dir():
    """yt-dlp looks for a binary literally named ``ffmpeg``/``ffmpeg.exe`` in
    the given directory, but ``imageio-ffmpeg`` ships a versioned name. Copy it
    once into a stable folder and hand that folder to yt-dlp.
    """
    src = imageio_ffmpeg.get_ffmpeg_exe()
    name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    dst_dir = os.path.join(
        os.path.expanduser("~"), ".youtubedownloader", "bin"
    )
    dst = os.path.join(dst_dir, name)

    if not os.path.exists(dst):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)

    return dst_dir


FFMPEG_DIR = _ffmpeg_dir()


class Control:
    @classmethod
    def _options(cls, output_dir, is_audio):
        options = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "ffmpeg_location": FFMPEG_DIR,
            "ignoreerrors": True,
            "noprogress": True,
            "quiet": True,
            "no_warnings": True,
        }

        if is_audio:
            options["format"] = "bestaudio/best"
            options["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            options["format"] = "bestvideo*+bestaudio/best"
            options["merge_output_format"] = "mp4"

        return options

    @classmethod
    def download(cls, url, output_dir, is_audio=False, playlist_subfolder=True):
        """Download a single video or a whole playlist.

        When ``playlist_subfolder`` is true, a playlist is saved into its own
        folder named after the playlist.

        Yields the file name of every finished download so the caller can
        update the UI and check for cancellation between items.
        """
        os.makedirs(output_dir, exist_ok=True)

        # First pass: resolve the URL without downloading so we know whether
        # it is a playlist and can iterate video by video.
        with YoutubeDL(
            {
                "extract_flat": "in_playlist",
                "ignoreerrors": True,
                "quiet": True,
                "no_warnings": True,
            }
        ) as ydl:
            info = ydl.extract_info(url, download=False)

        if info is None:
            raise RuntimeError(f"Could not read: {url}")

        if info.get("_type") == "playlist":
            entries = info.get("entries") or []
            if playlist_subfolder:
                folder = sanitize_filename(
                    info.get("title") or "playlist", restricted=False
                )
                output_dir = os.path.join(output_dir, folder)
                os.makedirs(output_dir, exist_ok=True)
        else:
            entries = [info]

        options = cls._options(output_dir, is_audio)
        with YoutubeDL(options) as ydl:
            for entry in entries:
                if not entry:
                    continue

                target = (
                    entry.get("webpage_url")
                    or entry.get("url")
                    or entry.get("id")
                )
                result = ydl.extract_info(target, download=True)

                if result is None:
                    yield f"Failed: {entry.get('title', target)}"
                    continue

                filename = ydl.prepare_filename(result)
                if is_audio:
                    filename = os.path.splitext(filename)[0] + ".mp3"

                yield os.path.basename(filename)

    @classmethod
    def open_output_path(cls, output_path):
        if not output_path or not os.path.exists(output_path):
            return

        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", output_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", output_path])
