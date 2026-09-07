<p align="center">
    <img src="/assets/icon.png" alt="Logo" width=200 height=200>
</p>

 # YoutubeDownloader

This is a simple Python desktop app to download YouTube videos and playlists!

## Functionalities

- Download YouTube videos by video URL
- Download YouTube playlists by playlist URL
- Set the output directory

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

## Building an Android APK

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
