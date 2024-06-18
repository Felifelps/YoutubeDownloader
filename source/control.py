import os
import platform
import subprocess

from pytube import Playlist, YouTube

class Control:
    @classmethod
    def download(cls, url, output_dir, is_playlist=False, is_audio=False):
        if "list=" in url:
            playlist = Playlist(url)
            output_dir = os.path.join(
                output_dir, playlist.title.split()[0]
            )
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            for video in playlist.videos:
                yield video.streams.filter(
                    only_audio=is_audio
                ).first().download(output_path=output_dir)
        else:
            video = YouTube(url)
            yield video.streams.filter(
                only_audio=is_audio
            ).first().download(output_path=output_dir)

    @classmethod
    def open_output_path(cls, output_path):
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", output_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", output_path])
