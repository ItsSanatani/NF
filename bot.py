from pyrogram import Client, filters
from nsfw_detector import predict
import ffmpeg
import os
from PIL import Image



from pyrogram import Client, filters
from nsfw_detector import predict
import ffmpeg
import os
from PIL import Image

# Telegram API क्रेडेंशियल्स
api_id = "28795512"
api_hash = "c17e4eb6d994c9892b8a8b6bfea4042a"
bot_token = "7893027318:AAHrAT8VukzZq3xUtAZuOuF2sKhhCok8gDg"

# NSFW मॉडल लोड करें
model = predict.load_model()

# Pyrogram क्लाइंट सेटअप
app = Client("nsfw_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# फोटो में NSFW डिटेक्शन
@app.on_message(filters.photo & filters.group)
async def photo_nsfw(client, message):
    photo_path = await message.download()
    result = predict.classify(model, photo_path)
    nsfw_score = result[photo_path]['nsfw']

    if nsfw_score >= 0.7:
        await message.delete()
        await message.reply_text("⚠️ NSFW फोटो डिटेक्ट की गई और हटा दी गई।")
    os.remove(photo_path)

# वीडियो और GIF में NSFW डिटेक्शन
@app.on_message((filters.video | filters.animation) & filters.group)
async def video_nsfw(client, message):
    video_path = await message.download()
    frame_path = "frame.jpg"
    try:
        # 1 सेकंड के बाद का फ्रेम निकालें
        ffmpeg.input(video_path, ss=1).output(frame_path, vframes=1).run(capture_stdout=True, capture_stderr=True)
        result = predict.classify(model, frame_path)
        nsfw_score = result[frame_path]['nsfw']

        if nsfw_score >= 0.7:
            await message.delete()
            await message.reply_text("⚠️ NSFW वीडियो/GIF डिटेक्ट किया गया और हटा दिया गया।")
    except Exception as e:
        print(e)
    finally:
        os.remove(video_path)
        if os.path.exists(frame_path):
            os.remove(frame_path)

# स्टिकर्स में NSFW डिटेक्शन
@app.on_message(filters.sticker & filters.group)
async def sticker_nsfw(client, message):
    sticker_path = await message.download()
    try:
        # WebP स्टिकर को JPEG में कन्वर्ट करें
        im = Image.open(sticker_path).convert("RGB")
        converted_path = "sticker.jpg"
        im.save(converted_path, "jpeg")
        result = predict.classify(model, converted_path)
        nsfw_score = result[converted_path]['nsfw']

        if nsfw_score >= 0.7:
            await message.delete()
            await message.reply_text("⚠️ NSFW स्टिकर डिटेक्ट किया गया और हटा दिया गया।")
    except Exception as e:
        print(e)
    finally:
        os.remove(sticker_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)

# बॉट रन करें
app.run()
