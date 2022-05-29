from telegram import *
from telegram.ext import *
from credentials import *
from string import punctuation
from collections import Counter
import re

data = "Okay, you convinced me. But I just tested and it does not seem to fail. My input"


def start(update: Update, context: CallbackContext):
    update.message.reply_text(f"Приветствую, я — {context.bot.first_name}. \n\nЯ умею анализировать текст, "
                              f"<b>пришлите фрагмент</b> и посмотрите на что я способен.", parse_mode=ParseMode.HTML)


def messagehandler(update: Update, context: CallbackContext):
    raw_txt = update.message.text
    sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', raw_txt)
    asent =
    words = raw_txt.split(' ')
    update.message.reply_text(f"Представляю вашему вниманию следующую статистику:\n\n"
                              f"• Количество предложений: <b>{len(sentences)}</b> \n"
                              f"<i>(из них: <b>{raw_txt.count('?')}</b> - вопросительных; "
                              f"<b>{raw_txt.count('!')}</b> - восклицательных)</i> \n"
                              f"• Брутто-слов: <b>{len(words)}</b>", parse_mode=ParseMode.HTML)


def error(update, context):
    update.message.reply_text('an error occurred')


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, messagehandler))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
