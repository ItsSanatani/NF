#api_id = "28795512"
#api_hash = "c17e4eb6d994c9892b8a8b6bfea4042a"
#bot_token = "7893027318:AAHrAT8VukzZq3xUtAZuOuF2sKhhCok8gDg"

from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import os
from moviepy.editor import VideoFileClip

# NSFW मॉडल लोड करें
model = hub.load('https://tfhub.dev/ashishb/nnfnets-c0-nsfw-classification/1')

def is_nsfw(image: Image.Image) -> bool:
    image = image.resize((224, 224)).convert('RGB')
    image_array = np.array(image) / 255.0
    image_array = image_array[np.newaxis, ...]
    predictions = model(image_array)
    nsfw_score = predictions[0][1].numpy()
    return nsfw_score > 0.7

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('नमस्ते! मैं इस ग्रुप में NSFW सामग्री का पता लगाकर उसे हटाने के लिए सक्रिय हूँ।')

def handle_photo(update: Update, context: CallbackContext) -> None:
    photo_file = update.message.photo[-1].get_file()
    photo_bytes = BytesIO(photo_file.download_as_bytearray())
    image = Image.open(photo_bytes)
    if is_nsfw(image):
        update.message.delete()
        context.bot.send_message(chat_id=update.effective_chat.id, text="NSFW फ़ोटो हटाई गई।")

def handle_video(update: Update, context: CallbackContext) -> None:
    video_file = update.message.video.get_file()
    video_path = os.path.join('/tmp', f"{video_file.file_id}.mp4")
    video_file.download(video_path)
    clip = VideoFileClip(video_path)
    for frame in clip.iter_frames(fps=1):
        image = Image.fromarray(frame)
        if is_nsfw(image):
            update.message.delete()
            context.bot.send_message(chat_id=update.effective_chat.id, text="NSFW वीडियो हटाया गया।")
            break
    clip.reader.close()
    os.remove(video_path)

def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    if document.mime_type in ['image/gif', 'video/mp4']:
        doc_file = document.get_file()
        doc_path = os.path.join('/tmp', f"{document.file_id}.mp4")
        doc_file.download(doc_path)
        clip = VideoFileClip(doc_path)
        for frame in clip.iter_frames(fps=1):
            image = Image.fromarray(frame)
            if is_nsfw(image):
                update.message.delete()
                context.bot.send_message(chat_id=update.effective_chat.id, text="NSFW GIF/स्टिकर हटाया गया।")
                break
        clip.reader.close()
        os.remove(doc_path)

def main():
    updater = Updater("7893027318:AAHrAT8VukzZq3xUtAZuOuF2sKhhCok8gDg", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    dispatcher.add_handler(MessageHandler(Filters.video, handle_video))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("image/gif"), handle_document))
    dispatcher.add_handler(MessageHandler(Filters.sticker, handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
