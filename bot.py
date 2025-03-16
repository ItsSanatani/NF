from pyrogram import Client, filters
from nsfw_detector import predict
import ffmpeg
import os
from PIL import Image

api_id = "28795512"
api_hash = "c17e4eb6d994c9892b8a8b6bfea4042a"
bot_token = "7893027318:AAHrAT8VukzZq3xUtAZuOuF2sKhhCok8gDg"

model = predict.load_model()

app = Client("nsfw_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# === NSFW Detection for Photos ===
@app.on_message(filters.photo & filters.group)
async def photo_nsfw(client, message):
    photo_path = await message.download()
    result = predict.classify(model, photo_path)
    nsfw_score = result[photo_path]['nsfw']

    if nsfw_score >= 0.7:
        await message.delete()
        await message.reply_text(f"⚠️ NSFW Photo Detected! Message removed.")
    os.remove(photo_path)

# === NSFW Detection for Videos & GIFs ===
@app.on_message((filters.video | filters.animation) & filters.group)
async def video_nsfw(client, message):
    video_path = await message.download()
    frame_path = "frame.jpg"
    try:
        # Extract frame
        ffmpeg.input(video_path, ss=1).output(frame_path, vframes=1).run(capture_stdout=True, capture_stderr=True)
        result = predict.classify(model, frame_path)
        nsfw_score = result[frame_path]['nsfw']

        if nsfw_score >= 0.7:
            await message.delete()
            await message.reply_text(f"⚠️ NSFW Video/GIF Detected! Message removed.")
    except Exception as e:
        print(e)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(frame_path):
            os.remove(frame_path)

# === NSFW Detection for Stickers ===
@app.on_message(filters.sticker & filters.group)
async def sticker_nsfw(client, message):
    sticker_path = await message.download()
    try:
        # Convert webp sticker to jpg
        im = Image.open(sticker_path).convert("RGB")
        converted_path = "sticker.jpg"
        im.save(converted_path, "jpeg")
        result = predict.classify(model, converted_path)
        nsfw_score = result[converted_path]['nsfw']

        if nsfw_score >= 0.7:
            await message.delete()
            await message.reply_text(f"⚠️ NSFW Sticker Detected! Message removed.")
    except Exception as e:
        print(e)
    finally:
        if os.path.exists(sticker_path):
            os.remove(sticker_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)

app.run()
