# -*- coding: utf-8 -*-
"""
Created on Thu May  7 18:08:12 2026

@author: Dmytro
"""
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
#from langchain_chroma import Chroma
#from langchain_core.runnables import RunnablePassthrough
#from langchain_core.output_parsers import StrOutputParser
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
import os
import nest_asyncio
import sys
sys.path.insert(1, os.getcwd() + '/tools/email')
sys.path.insert(1, os.getcwd() + '/tools/db')
from email_tool import email_tool
from db_tool import citrus_search_tool, ordering_tool

class TelegramAIBot:
    
    def __init__(self, auth_token: str, agent: AgentExecutor):
        self.app = Application.builder().token(auth_token).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.process_message))
        self.agent = agent
        #self.prompt = prompt
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
        response = self.agent.invoke({"input" : "\n".join(self.conversation_history[chat_id] + [message])})['output']
        print('User\'s message:\n' + message)
        print('LLM\'s response:\n' + response)
        await update.message.reply_text(response)
        self.conversation_history[chat_id].append('Clementine: ' + response)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Your name is Clementine and you are a Telegram chatbot, 
that assists customers of a citrus nursery with choosing and ordering a citrus 
tree. You are only going to be asked questions about citruses, if you are asked 
something different ignore such question by simply replying that you only answer 
questions about citruses. If you receive /start message greet the customer, 
introduce yourself and offer help, if you receive /help message say that you're 
here to assist with choosing a citrus tree and ask about which citrus tree a 
customer wants.Use  citrus_search_tool to search for citruses, that are 
for sale in a nursery. If customer wants to make an order, ask him for his name, 
email and citrus trees he wants to order, then create an order use ordering_tool. 
After creating an order send an order confirmation email to a customer with his 
order id, using email_tool. 
Try to keep your generated messages as short as possible, 
especially replies for /start and /help, remember - it's a chat in Telegram.
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")])

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
tools = [email_tool, citrus_search_tool, ordering_tool]
agent = create_tool_calling_agent(llm = llm, prompt = prompt, tools = tools)
agent_executor = AgentExecutor(agent = agent, tools = tools, verbose = True)
nest_asyncio.apply()
telegram_ai_bot = TelegramAIBot(os.environ['TELEGRAM_AUTH_TOKEN'], 
                                agent_executor)
telegram_ai_bot.start_polling()
#def main():
#    app = ApplicationBuilder().token(os.environ['TELEGRAM_AUTH_TOKEN']).build()
#    app.run_polling()
#if(__name__ == '__main__'):
#    main()