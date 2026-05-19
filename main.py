# -*- coding: utf-8 -*-
"""
Created on Thu May  7 18:08:12 2026

@author: Dmytro
"""
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
#from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
#from langchain_chroma import Chroma
#from langchain_core.runnables import RunnablePassthrough
#from langchain_core.output_parsers import StrOutputParser
import os
import nest_asyncio
import sys
sys.path.insert(1, os.getcwd() + '/tools/email')
from email_tool import email_tool

class TelegramAIBot:
    
    def __init__(self, auth_token: str, llm: ChatHuggingFace, prompt: str):
        self.app = Application.builder().token(auth_token).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.process_message))
        self.llm = llm
        self.prompt = prompt
        self.conversation_history = {}
        
    def start_polling(self):
        print('About to start polling.')
        self.app.run_polling(1)
        print('Polling started.')

    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print('Message received. Begining processing...')
        message = update.message.text
        chat_id = update.message.chat.id
        if(not (chat_id in self.conversation_history.keys())):
            self.conversation_history[chat_id] = ['User: ' + message]
        else:
            self.conversation_history[chat_id].append('User: ' + message)
        if(len(self.conversation_history[chat_id])>10):
            self.conversation_history[chat_id].pop(0)
            self.conversation_history[chat_id].pop(0)
        print(self.conversation_history[chat_id])
        response = self.llm.invoke(prompt.format(
            '\n'.join(self.conversation_history[chat_id]), message)).content
        print('User\'s message:\n' + message)
        print('LLM\'s response:\n' + response)
        await update.message.reply_text(response)
        self.conversation_history[chat_id].append('Clementine: ' + response)

prompt = """Your name is Clementine and you are a telegram chatbot, 
that assists customers of a citrus nursery with choosing a citrus tree. 
You are only going to be asked questions about citruses, if you are asked 
something different ignore such question by simply replying that you only answer 
questions about citruses. If you receive /start message greet the customer, 
introduce yourself and offer help, if you receive /help message say that you're 
here to assist with choosing a citrus tree and ask about which citrus tree a 
customer wants.Here are the last messages from conversation for you to understand
context:{}. Try to keep your generated messages as short as possible, 
especially replies for /start and /help, remember - it's a chat in Telegram.
Reply to a message specified below. 
Message: {}
"""

llm = ChatHuggingFace(llm = HuggingFaceEndpoint(repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                     #repo_id="HuggingFaceH4/zephyr-7b-alpha"
                     huggingfacehub_api_token = os.environ['HF_API_KEY'],
                     temperature = 0.5,
                     max_new_tokens = 512
                     #provider = "featherless-ai",
                     #task="conversational"
                     ))
#result = llm.invoke(prompt.format('I can\'t choose between Valencia and Washington Navel orange...'))
#print(result.content)
print(type(email_tool))
nest_asyncio.apply()
telegram_ai_bot = TelegramAIBot(os.environ['TELEGRAM_AUTH_TOKEN'], llm, prompt)
telegram_ai_bot.start_polling()
#def main():
#    app = ApplicationBuilder().token(os.environ['TELEGRAM_AUTH_TOKEN']).build()
#    app.run_polling()
#if(__name__ == '__main__'):
#    main()