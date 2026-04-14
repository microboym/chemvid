import os
import asyncio
import edge_tts
from moviepy import ImageClip, TextClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

FONT_PATH = "./font.ttf"
RESOLUTION = (540, 960) # Lower resolution for faster MVP rendering on small servers

async def generate_tts(text: str, output_path: str):
    """Generates Chinese TTS audio using Microsoft Edge TTS."""
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(output_path)

def create_segment(image_path, text, audio_path):
    """Creates a single video segment combining image, text, and TTS audio."""
    # 1. Load Audio
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # 2. Load and format Image (Center crop to vertical output resolution)
    img_clip = ImageClip(image_path)
    # Resize height first, then crop to the target vertical width.
    img_clip = img_clip.resized(height=RESOLUTION[1]).cropped(x_center=img_clip.w/2, width=RESOLUTION[0])
    img_clip = img_clip.with_duration(duration)

    # 3. Create Chinese Text Overlay
    txt_clip = TextClip(
        font=FONT_PATH,
        text=text,
        font_size=60,
        color='white',
        method='caption',
        size=(650, None) # Auto-wrap text
    )
    txt_clip = txt_clip.with_position(('center', 'bottom')).with_duration(duration)

    # 4. Composite together
    video_segment = CompositeVideoClip([img_clip, txt_clip])
    video_segment = video_segment.with_audio(audio_clip)

    return video_segment

def build_product_video(task_id: str, data: dict):
    """The main pipeline to stitch the video together."""
    output_filename = f"./outputs/output_{task_id}.mp4"

    # Prepare texts based on the "Template 1" spec
    hook_text = f"{data['application_area']}行业痛点：品质不稳定？供应不及时？"
    intro_text = f"{data['product_name']}\n适用于{data['application_area']}"
    selling_text = data['selling_points'] # Assuming a comma separated string for MVP
    brand_text = f"{data['company_name']} 欢迎合作"

    # Define paths for temporary audio
    audio_paths = [f"./uploads/audio_{task_id}_{i}.mp3" for i in range(4)]

    # Generate TTS files (Run async loop synchronously inside this background task thread)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(
        generate_tts(hook_text, audio_paths[0]),
        generate_tts(intro_text, audio_paths[1]),
        generate_tts(selling_text, audio_paths[2]),
        generate_tts(brand_text, audio_paths[3])
    ))

    # Create Video Segments
    # Assuming the frontend sent us 3 image paths: bg_img, product_img, logo_img
    clip1 = create_segment(data['bg_img'], hook_text, audio_paths[0])
    clip2 = create_segment(data['product_img'], intro_text, audio_paths[1])
    clip3 = create_segment(data['product_img'], selling_text, audio_paths[2]) # Reuse product img for selling points
    clip4 = create_segment(data['logo_img'], brand_text, audio_paths[3])

    # Concatenate all clips
    final_video = concatenate_videoclips([clip1, clip2, clip3, clip4], method="compose")

    # Export (Limit bitrate and use fast preset)
    final_video.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="1200k",
        preset="ultrafast",
        threads=1
    )

    # Clean up memory and temp audio
    final_video.close()
    for path in audio_paths:
        if os.path.exists(path):
            os.remove(path)

    return output_filename
