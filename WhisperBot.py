#!/usr/bin/env python

#
#  SPDX-FileCopyrightText 2023 Davide Garberi <dade.garberi@gmail.com>
#
#  SPDX-License-Identifier: GPL-3.0-or-later
#

import logging, sys, io, time
import telegram.error
import nest_asyncio

from faster_whisper import WhisperModel
from telegram import Chat, ForceReply, Message, Update
from telegram.constants import FloodLimit, MessageLimit
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

nest_asyncio.apply()

model_size = "medium"

base = WhisperModel("base", device="auto", compute_type="auto")
small = WhisperModel("small", device="auto", compute_type="auto")
medium = WhisperModel("medium", device="auto", compute_type="auto")

model_dict = {
    "base": base,
    "small": small,
    "medium": medium,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Whisper Transcribe Bot!\n"
        "With this bot you can transcribe audio messages, using the OpenAI Whisper neural net.\n"
        "You can run this bot in private chat, just by sending a voice message, or add it in groups.\n"
        "Type /help for a list of commands\n"
        "Bot made by DD3Boh."
    );

async def update_transcription(buf: io.BytesIO):
    texts = [""]; i = 0; prev = 0.0
    interval = (90 / FloodLimit.MESSAGES_PER_MINUTE_PER_GROUP)
    segments, info = model_dict.get(model_size).transcribe(buf, beam_size=1, initial_prompt="Transcribe audio, with proper punctuation.")

    for segment in segments:
        if (len(texts[i] + segment.text) < MessageLimit.MAX_TEXT_LENGTH):
            texts[i] += segment.text
        else:
            i += 1
            texts.insert(i, segment.text)

        while (time.time() - prev >= interval):
            prev = time.time()
            yield texts
    else:
        yield texts

async def transcribe_work(user_msg: Message) -> None:
    text = ""; k = 0

    msg = await user_msg.reply_text("Downloading...\n", quote=True)

    audio_file = await user_msg.effective_attachment.get_file()
    buf = io.BytesIO()
    await audio_file.download_to_memory(buf)
    buf.seek(0)

    await msg.edit_text("Transcribing audio...\n")

    async for texts in update_transcription(buf):
        for i in range(len(texts)):
            if i > k:
                msg = await msg.reply_text(texts[i], quote=True)
                k = i
            else:
                await msg.edit_text(texts[i])

async def transcribe_private(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (update.effective_chat.type != Chat.PRIVATE):
        return

    user_msg = update.message

    await transcribe_work(user_msg)

async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_msg = update.message.reply_to_message

    await transcribe_work(user_msg)

def main() -> None:
    application = Application.builder().token(sys.argv[1]).read_timeout(10).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("transcribe", transcribe_command))

    application.add_handler(MessageHandler(filters.AUDIO | filters.VIDEO_NOTE | filters.VOICE, transcribe_private))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
