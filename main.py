# coding=utf-8
from telegram import *
from telegram.ext import *
from credentials import *
import os
import re
import docx2txt
import matplotlib
import pymorphy2 as pm
import matplotlib.pyplot as plt


# TODO: .docx, .doc, .txt reading

# Used:
# https://docs.python.org/3/library/re.html
# https://pymorphy2.readthedocs.io/en/stable/
# https://docs.python-telegram-bot.org/en/v20.0a0/
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html


def analysis(text):
    # list with sentences
    sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    # list with length of sentences
    sentences_l = [len(i.split(' ')) for i in sentences]
    # list with words
    words = text.split(' ')
    # cleaning everything except for letters
    words = [i for i in ["".join(filter(str.isalpha, k)) for k in words] if i != '']
    # parsing lems & removing stop words
    morph = pm.MorphAnalyzer()
    netto_words = [x for x in [morph.parse(x)[0].normal_form for x in words]
                   if x not in open("stop-ru.txt").read().split()]
    # list with length of netto-words
    netto_words_l = [len(i) for i in netto_words]
    # creating and sorting a frequency dict
    frequency = {}
    for i in netto_words:
        if frequency.get(i):
            frequency[i] += 1
        else:
            frequency[i] = 1
    frequency_sorted = (dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True)))
    frequency_output = [k for k in list(frequency_sorted.items())[:10] if k[1] > 1]

    # Graphical output of words frequency

    if frequency_output:
        fig, ax = plt.subplots()

        # getting cords
        y = list(range(len(frequency_output)))
        x = [k[1] for k in frequency_output]
        tick_label = [k[0] for k in frequency_output]

        # adjusting axis's
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xticks(range(0, max(x) + 1, round(max(x) / 10) if round(max(x) / 10) > 1 else 1))

        bars = ax.barh(y, x, tick_label=tick_label)

        for bar in bars:
            ax.text(bar.get_width() + 0.05 * bars[0].get_width(), bar.get_y() + 0.25, bar.get_width(),
                    horizontalalignment='center', color=bars[0].get_facecolor(), weight='bold')

        fig.tight_layout()
        plt.savefig('graph.png', transparent=True, dpi=800)

    # Text output of words frequency

    strfrq = ''
    for i, v in [k for k in frequency_output]:
        strfrq += f'{i} : {v}\n'
    nodata = "недостаточно данных"

    # finalising
    text = f"Представляю вашему вниманию следующую статистику:\n\n" \
           f"• Количество предложений: <b>{len(sentences)}</b> \n" \
           f"<i>(из них: <b>{text.count('?')}</b> - вопросительных; " \
           f"<b>{text.count('!')}</b> - восклицательных)</i>\n" \
           f"• Средняя длина предложения: <b>{round(sum(sentences_l) / len(sentences_l), 1)}</b> слов\n" \
           f"• Количество слов: <b>{len(words)}-{len(netto_words)}</b>\n" \
           f"<i>(вода: <b>{round(100 - len(netto_words) / len(words) * 100, 1)}%</b>)</i>\n" \
           f"• Средняя длина слова: <b>{round(sum(netto_words_l) / len(netto_words_l), 1)}</b> букв.\n\n" \
           f"Часто используемые слова: \n{strfrq if strfrq else nodata}"
    return text


def start(update: Update, context: CallbackContext):
    update.message.reply_text(f"Приветствую, я — <b>{context.bot.first_name}</b>. \n\nЯ умею анализировать текст, "
                              f"пришлите фрагмент или <i>.txt .docx</i> файл и <b>посмотрите</b> на что я способен.",
                              parse_mode=ParseMode.HTML)


def downloader(update, context):
    file = context.bot.get_file(update.message.document).download()
    update.message.reply_text("Запрос принят в обработку, пожалуйста подождите...")
    if file.split('.')[1] == "docx":
        update.message.reply_text(analysis(docx2txt.process(file)), parse_mode=ParseMode.HTML)
    elif file.split('.')[1] == "doc":
        update.message.reply_text(analysis(docx2txt.process(file)), parse_mode=ParseMode.HTML)
    elif file.split('.')[1] == "txt":
        update.message.reply_text(analysis(open(file, encoding='utf-8').read()), parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text('Неверный формат, используйте .txt или .docx')

    if os.path.exists('graph.png'):
        update.message.reply_photo(open('graph.png', 'rb'))
        os.remove('graph.png')
    os.remove(file)


def messagehandler(update: Update, context: CallbackContext):
    update.message.reply_text("Запрос принят в обработку, пожалуйста подождите...")
    update.message.reply_text(analysis(update.message.text), parse_mode=ParseMode.HTML)
    if os.path.exists('graph.png'):
        update.message.reply_photo(open('graph.png', 'rb'))
        os.remove('graph.png')


def error(update, context):
    update.message.reply_text('an error occurred')


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, messagehandler))
    dispatcher.add_handler(MessageHandler(Filters.document, downloader))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    matplotlib.rc('font', **{'sans-serif': 'Ubuntu', 'family': 'sans-serif', 'size': 12})
    main()
