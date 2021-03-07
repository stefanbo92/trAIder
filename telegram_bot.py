from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time
from scraper_check import *

def start(update: Update, context: CallbackContext) -> None:
    count=0
    update.message.reply_text(f'Hello {update.effective_user.first_name}. Starting telegram bot to check scraping..')
    print("Starting telegram bot to check scraping...")
    number_news = check_news_available()
    number_prices = check_index_prices()
    print("News available:", number_news)
    print("Prices available:", number_prices)
    if (number_news>0 and number_prices>0):
        print("everything is fine")
        update.message.reply_text(f'everything is fine \nscraped news: '+str(number_news)+'\nscraped index prices: '+str(number_prices))
    else:
        print("Warning no data was scraped!!")
        update.message.reply_text(f'Warning no data was scraped!')


updater = Updater('1445895754:AAFbd731kEdlRWlamRuQlwAE_6NFviuVLwc')

updater.dispatcher.add_handler(CommandHandler('start', start))

updater.start_polling()
updater.idle()