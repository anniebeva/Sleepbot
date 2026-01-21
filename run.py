from bot import bot
import handlers.sleep
import handlers.notes
import handlers.stats
import handlers.delete
import handlers.edit
import handlers.start
import handlers.show

if __name__ == "__main__":
    bot.polling()