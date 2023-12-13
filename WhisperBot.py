#!/usr/bin/env python

#
#  SPDX-FileCopyrightText 2023 Davide Garberi <dade.garberi@gmail.com>
#
#  SPDX-License-Identifier: GPL-3.0-or-later
#

import logging, sys

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Whisper Transcribe Bot!\n"
        "With this bot you can transcribe audio messages, using the OpenAI Whisper neural net.\n"
        "You can run this bot in private chat, just by sending a voice message, or add it in groups.\n"
        "Type /help for a list of commands\n"
        "Bot made by DD3Boh."
    );

def main() -> None:
    application = Application.builder().token(sys.argv[1]).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
