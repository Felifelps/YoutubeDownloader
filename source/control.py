import glob
import os
import platform
import shutil
import subprocess

from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename

from .env import is_android

try:
    import imageio_ffmpeg
except ImportError:  # not bundled on mobile builds
    imageio_ffmpeg = None

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


def _android_ffmpeg_dir():
    """On Android there is no ffmpeg unless one is shipped with the app. Look
    for an arm64 binary at ``assets/ffmpeg`` (or the ``YTDL_FFMPEG`` env var),
    copy it somewhere executable and return that folder. ``None`` if absent.
    """
    for src in (os.environ.get("YTDL_FFMPEG"), os.path.join(_ASSETS_DIR, "ffmpeg")):
        if not src or not os.path.isfile(src):
            continue
        dst_dir = os.path.join(os.getcwd(), ".bin")
        dst = os.path.join(dst_dir, "ffmpeg")
        try:
            os.makedirs(dst_dir, exist_ok=True)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                os.chmod(dst, 0o755)
            return dst_dir
        except OSError:
            return None
    return None


def _ffmpeg_dir():
    """Return a folder holding a binary literally named ``ffmpeg``/``ffmpeg.exe``
    for yt-dlp to use, or ``None`` when no usable ffmpeg is available.
    """
    if is_android():
        return _android_ffmpeg_dir()

    if imageio_ffmpeg is None:
        return None

    try:
        src = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

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
HAS_FFMPEG = FFMPEG_DIR is not None


class Control:
    @classmethod
    def _options(cls, output_dir, is_audio):
        options = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "ignoreerrors": True,
            "noprogress": True,
            "quiet": True,
            "no_warnings": True,
            "overwrites": False,  # never re-download an existing file
        }

        if HAS_FFMPEG:
            options["ffmpeg_location"] = FFMPEG_DIR
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
        else:
            # No ffmpeg: grab a single already-muxed stream so nothing needs
            # merging or transcoding.
            options["format"] = (
                "bestaudio[ext=m4a]/bestaudio" if is_audio else "best"
            )

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

                # Skip anything already downloaded (same title -> any extension)
                # so re-running a URL doesn't create duplicates.
                title = entry.get("title")
                if title:
                    stem = os.path.join(
                        output_dir, sanitize_filename(title, restricted=False)
                    )
                    existing = [
                        p
                        for p in glob.glob(glob.escape(stem) + ".*")
                        if not p.endswith((".part", ".ytdl"))
                    ]
                    if existing:
                        yield f"Already downloaded: {os.path.basename(existing[0])}"
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
                if is_audio and HAS_FFMPEG:
                    filename = os.path.splitext(filename)[0] + ".mp3"

                yield os.path.basename(filename)

    @classmethod
    def open_output_path(cls, output_path):
        if is_android():
            return  # no file manager intent from here
        if not output_path or not os.path.exists(output_path):
            return

        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", output_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", output_path])
