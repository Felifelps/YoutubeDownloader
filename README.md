<p align="center">
    <img src="/assets/icon.png" alt="Logo" width=200 height=200>
</p>

 # YoutubeDownloader

A small Python + Flet app to download YouTube videos and playlists, on desktop
and Android. The downloading is handled by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

> Personal use only. Please read the [DISCLAIMER](DISCLAIMER.md).

## Download

Grab the latest **Windows bundle** or **Android APK** from the
[Releases page](https://github.com/Felifelps/YoutubeDownloader/releases).

- **Windows**: unzip and run `YoutubeDownloader.exe`.
- **Android**: install the `.apk` (`armeabi-v7a`, Android 5.0+); you'll need to
  allow installing from unknown sources. Audio saves as `.m4a`; video needs an
  arm64 `ffmpeg` binary bundled at build time (see below).

## Functionalities

- Download YouTube videos by video URL
- Download YouTube playlists by playlist URL (into a folder named after the playlist)
- Multiple URLs at once (one per line); already-downloaded files are skipped
- Choose video or audio
- Set the output directory (desktop)

## Technologies

- Python
- Flet
- yt-dlp
- ffmpeg (bundled on desktop via `imageio-ffmpeg`)

## Installation

To install this project, follow these steps:

1. If you haven't already, install Python on your machine on [this link](https://python.org).

2. Clone this project with:

    ```shell
    git clone https://github.com/Felifelps/YoutubeDownloader
    ```

3. Create and activate a virtual environment in the project directory:

    - On Windows:
    ```shell
    python -m venv .venv
    .venv\Scripts\Activate
    ```

    - On Linux:
    ```shell
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4. Install the requirements with:

    ```shell
    pip install -r requirements.txt
    ```

5. Run the project with:

    ```shell
    python main.py
    ```

## Building a Windows bundle

```shell
pip install pyinstaller pillow
flet pack main.py -D --name YoutubeDownloader --icon assets/icon.png
```

Output is a folder in `dist/YoutubeDownloader/` — zip it for distribution.

## Building an Android APK

Use the helper script (`armeabi-v7a`, ~29 MB):

```powershell
.\build_apk.ps1
```

Or call `flet build` directly. It uses the dependencies in `pyproject.toml`
(not `requirements.txt`), so `flet-desktop` and the desktop ffmpeg are left out
of the bundle.

The app can be packaged with `flet build apk`. `flet build` uses the
dependencies in `pyproject.toml` (not `requirements.txt`), so `flet-desktop`
and the desktop ffmpeg are left out of the bundle.

### 1. Install the toolchain (one time)

- **JDK 17** – e.g. [Temurin 17](https://adoptium.net/temurin/releases/?version=17).
  Set `JAVA_HOME` to point at it.
- **Flutter SDK (stable)** – <https://docs.flutter.dev/get-started/install/windows>.
  Add `flutter\bin` to `PATH`.
- **Android SDK** – install Android Studio, then in *SDK Manager* add
  "Android SDK Command-line Tools", "Platform-Tools" and an SDK Platform
  (API 34+). Set `ANDROID_HOME` (e.g. `%LOCALAPPDATA%\Android\Sdk`).
- Accept licenses: `flutter doctor --android-licenses`
- Check everything: `flutter doctor` and `flet doctor`

### 2. Build

```shell
flet build apk --verbose
```

The APK is written to `build\apk\app-release.apk`. Copy it to a phone and
install it (enable "install from unknown sources").

### 3. Notes / limitations on Android

- **Audio downloads work out of the box.** They are saved as `.m4a` (no
  transcoding to mp3, since that needs ffmpeg).
- **Video downloads need ffmpeg.** YouTube serves video and audio as separate
  streams that must be merged. Ship an arm64 `ffmpeg` binary at
  `assets/ffmpeg` before building and it will be picked up automatically;
  without it, video downloads fail with "Requested format is not available".
- Files are saved to `/sdcard/Download/YoutubeDownloader`. The download folder
  is fixed (no directory picker on Android). Grant the storage permission when
  prompted.

## Contribution

Fork this repo and make a pull request with your alterations, and I'll review it as soon as possible.
