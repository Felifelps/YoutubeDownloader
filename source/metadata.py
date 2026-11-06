"""Write audio tags (cover, artist, album, composer, ...) without ffmpeg.

On Android there is no ffmpeg binary, so yt-dlp's ``FFmpegMetadata`` /
``EmbedThumbnail`` post-processors can't run. This module does the same job
with `mutagen <https://mutagen.readthedocs.io/>`_, a pure-python tag editor
that works anywhere Python runs: it copies the fields yt-dlp discovered into
the file's tags and embeds the cover art.

It supports the container types YouTube actually serves when ffmpeg is not
available (MP4/M4A, MP3, FLAC, Ogg Vorbis/Opus). Anything else is left alone.
"""

import base64
import datetime
import urllib.request

try:
    from mutagen import flac, id3, mp4, oggopus, oggvorbis

    _HAS_MUTAGEN = True
except ImportError:  # pragma: no cover
    _HAS_MUTAGEN = False


_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) YoutubeDownloader"
)
_MAX_COVER_BYTES = 20 * 1024 * 1024


def _image_mime(data):
    """Guess the mime type of an image from its magic bytes, or ``None``."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"GIF8"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def _thumbnail_size(item):
    """Return the area (w*h) a thumbnail documents, or 0 when unknown."""
    width = item.get("width") or 0
    height = item.get("height") or 0
    if width and height:
        return width * height
    resolution = str(item.get("resolution") or "")
    parts = resolution.lower().split("x")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]) * int(parts[1])
    return 0


def _thumbnail_urls(info):
    """Cover urls from a yt-dlp info dict, best first.

    Jpg/png files are ranked above webp/gif (better player support) and
    bigger images above smaller ones. Duplicate urls are dropped.
    """
    def score(item):
        url = item.get("url") or ""
        path = url.split("?", 1)[0].lower()
        if path.endswith((".jpg", ".jpeg")):
            fmt = 2
        elif path.endswith(".png"):
            fmt = 1
        else:
            fmt = 0
        return (fmt, _thumbnail_size(item))

    seen = set()
    urls = []
    for item in sorted(
        info.get("thumbnails") or [], key=score, reverse=True
    ):
        url = item.get("url") if isinstance(item, dict) else None
        if not url or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def download_cover(info, max_tries=5, timeout=15):
    """Download the best cover art for ``info``, or ``None``.

    Several thumbnails are tried in turn (YouTube sometimes serves a generic
    placeholder for missing covers) and the first one whose download succeeds
    and whose bytes look like an image is returned.
    """
    for url in _thumbnail_urls(info)[:max_tries]:
        request = urllib.request.Request(
            url, headers={"User-Agent": _USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read(_MAX_COVER_BYTES)
        except Exception:
            continue
        if data and _image_mime(data):
            return data
    return None


def _strings(value):
    """Normalise a possibly-scalar/list value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        result = []
        for item in value:
            if isinstance(item, dict):
                item = item.get("name") or item.get("artist")
            if item:
                result.append(str(item))
        return result
    return [str(value)]


def _metadata(info):
    """Extract the tag fields mutagen needs from a yt-dlp info dict."""
    date = info.get("release_date") or info.get("upload_date")
    if not date and info.get("timestamp"):
        timestamp = info["timestamp"]
        date = datetime.datetime.fromtimestamp(
            int(timestamp), datetime.timezone.utc
        ).strftime("%Y%m%d")
    if date and len(date) == 8 and date.isdigit():
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    track = info.get("track_number")
    try:
        track = str(int(track)) if track is not None else None
    except (TypeError, ValueError):
        track = None

    artist = info.get("artist") or info.get("creator") or info.get("uploader")
    return {
        "title": info.get("title"),
        "artist": _strings(artist),
        "album_artist": _strings(info.get("album_artist")),
        "album": info.get("album"),
        "composer": _strings(info.get("composer") or info.get("composers")),
        "genre": info.get("genre"),
        "date": date,
        "track": track,
        "description": info.get("description"),
    }


def _apply_vorbis(tags, meta, image, mime):
    if meta["title"]:
        tags["title"] = [meta["title"]]
    for key in ("artist", "album_artist", "composer", "genre"):
        if meta[key]:
            tags[key] = meta[key]
    if meta["album"]:
        tags["album"] = [meta["album"]]
    if meta["date"]:
        tags["date"] = [meta["date"]]
    if meta["track"]:
        tags["tracknumber"] = [meta["track"]]
    if meta["description"]:
        tags["description"] = [meta["description"]]
    if image:
        # Ogg stores cover art as a base64 image block (FLAC-style).
        from mutagen.flac import Picture

        picture = Picture()
        picture.type = 3  # front cover
        picture.mime = mime
        picture.desc = "Cover"
        picture.data = image
        tags["metadata_block_picture"] = [
            base64.b64encode(picture.write()).decode("ascii")
        ]


def write_tags(path, info, image_data=None):
    """Write the title/artist/album/... and cover into ``path``.

    ``image_data`` is the raw cover art; when ``None`` it is downloaded from
    ``info``. Returns ``True`` when tags were written, ``False`` when the file
    type is unsupported or mutagen is unavailable.
    """
    if not _HAS_MUTAGEN:
        return False

    image_data = image_data if image_data is not None else download_cover(info)
    mime = _image_mime(image_data) if image_data else None
    meta = _metadata(info)

    # Pick a tagger for the actual file format.
    from mutagen import File as _MutagenFile

    audio = _MutagenFile(path, easy=False)

    if audio is None:
        return False

    if isinstance(audio, mp4.MP4):
        return _write_mp4(audio, path, meta, image_data, mime)
    if isinstance(audio, id3.ID3FileType):
        return _write_id3(audio, path, meta, image_data, mime)
    if isinstance(audio, flac.FLAC):
        return _write_flac(audio, path, meta, image_data, mime)
    if isinstance(audio, (oggopus.OggOpus, oggvorbis.OggVorbis)):
        _apply_vorbis(audio.tags, meta, image_data, mime)
        audio.save()
        return True

    return False


def _write_id3(audio, path, meta, image_data, mime):
    tags = audio.tags if audio.tags is not None else id3.ID3()

    if meta["title"]:
        tags.add(id3.TIT2(encoding=3, text=meta["title"]))
    for artist in meta["artist"]:
        tags.add(id3.TPE1(encoding=3, text=artist))
    for artist in meta["album_artist"]:
        tags.add(id3.TPE2(encoding=3, text=artist))
    for composer in meta["composer"]:
        tags.add(id3.TCOM(encoding=3, text=composer))
    if meta["album"]:
        tags.add(id3.TALB(encoding=3, text=meta["album"]))
    if meta["genre"]:
        tags.add(id3.TCON(encoding=3, text=meta["genre"]))
    if meta["date"]:
        tags.add(id3.TDRC(encoding=3, text=meta["date"]))
    if meta["track"]:
        tags.add(id3.TRCK(encoding=3, text=meta["track"]))
    if meta["description"]:
        tags.add(id3.COMM(encoding=3, lang="eng", desc="", text=meta["description"]))
    if image_data and mime:
        tags.delall("APIC")
        tags.add(
            id3.APIC(encoding=3, mime=mime, type=3, desc="Cover", data=image_data)
        )

    # v2.3 is the most widely supported tag version across players.
    tags.save(path, v2_version=3)
    return True


def _write_mp4(audio, path, meta, image_data, mime):
    if meta["title"]:
        audio["\xa9nam"] = [meta["title"]]
    if meta["artist"]:
        audio["\xa9ART"] = meta["artist"]
    if meta["album_artist"]:
        audio["aART"] = meta["album_artist"]
    if meta["composer"]:
        audio["\xa9wrt"] = meta["composer"]
    if meta["album"]:
        audio["\xa9alb"] = [meta["album"]]
    if meta["genre"]:
        audio["\xa9gen"] = [meta["genre"]]
    if meta["date"]:
        audio["\xa9day"] = [meta["date"]]
    if meta["track"]:
        try:
            audio["trkn"] = [(int(meta["track"]), 0)]
        except ValueError:
            pass
    if meta["description"]:
        audio["desc"] = [meta["description"]]
    if image_data and mime:
        if mime == "image/png":
            cover_format = mp4.MP4Cover.FORMAT_PNG
        else:
            cover_format = mp4.MP4Cover.FORMAT_JPEG
        audio["covr"] = [mp4.MP4Cover(image_data, imageformat=cover_format)]

    audio.save()
    return True


def _write_flac(audio, path, meta, image_data, mime):
    if meta["title"]:
        audio["title"] = [meta["title"]]
    if meta["artist"]:
        audio["artist"] = meta["artist"]
    if meta["album_artist"]:
        audio["albumartist"] = meta["album_artist"]
    if meta["composer"]:
        audio["composer"] = meta["composer"]
    if meta["album"]:
        audio["album"] = [meta["album"]]
    if meta["genre"]:
        audio["genre"] = [meta["genre"]]
    if meta["date"]:
        audio["date"] = [meta["date"]]
    if meta["track"]:
        audio["tracknumber"] = [meta["track"]]
    if meta["description"]:
        audio["description"] = [meta["description"]]
    if image_data and mime:
        picture = flac.Picture()
        picture.type = 3
        picture.mime = mime
        picture.desc = "Cover"
        picture.data = image_data
        audio.clear_pictures()
        audio.add_picture(picture)

    audio.save()
    return True