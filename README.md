# 智化推 (Zhi Hua Tui) - MVP

Zhi Hua Tui is a lightweight prototype/MVP for automatically generating vertical promotional short videos for small and medium-sized enterprises (SMEs) in the chemical industry.

By uploading a few images and filling out a simple form, the system automatically stitches together a 15-20 second professional-looking video complete with Chinese AI voiceovers (TTS), text overlays, and transitions.

## Tech Stack
- **Backend:** FastAPI (with `BackgroundTasks` for async rendering)
- **Frontend:** Vanilla HTML/JS with Bootstrap 5
- **Video Processing:** MoviePy 2.0
- **Audio Generation:** `edge-tts` (Microsoft Edge TTS engine - free, high quality, no API keys needed)

## Prerequisites

### 1. Install ImageMagick
MoviePy requires ImageMagick to generate text overlays (like subtitles).
- **macOS:** `brew install imagemagick`
- **Ubuntu/Debian:** `sudo apt-get install imagemagick`

### 2. Add a Chinese Font
To render Chinese characters correctly on the video, you need a TrueType Font file.
- Download a free Chinese font (e.g., [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) or Alibaba PuHuiTi).
- Rename the file to `font.ttf`.
- Place it directly in the root directory of this project (`chemvid/font.ttf`).

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd chemvid
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install fastapi uvicorn moviepy edge-tts python-multipart
   ```

4. Ensure the temporary directories exist (they are used to store uploads and generated videos):
   ```bash
   mkdir -p uploads outputs
   ```

## Running the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

Then, open your web browser and navigate to:
**http://localhost:8000**

## How to Use
1. Open the web interface.
2. Fill in the company information, product name, and selling points.
3. Upload three images: a background/industry image, a product image, and a company logo.
4. Click "一键生成短视频" (Generate Video).
5. Wait for the background task to complete processing (usually 1-2 minutes depending on your CPU).
6. The generated MP4 video will appear on the screen, ready to be previewed or downloaded.

## Project Structure
- `main.py` - FastAPI application, routing, file uploading, and background task management.
- `video_engine.py` - Core logic for generating TTS audio and stitching the video/text/audio together using MoviePy.
- `static/index.html` - The frontend user interface.
- `font.ttf` - (User provided) Font file for rendering Chinese text.
- `uploads/` - Temporary storage for uploaded user images and generated MP3 files.
- `outputs/` - Storage for the final generated `.mp4` video files.