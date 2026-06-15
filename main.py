# -*- coding: utf-8 -*-
"""
Created on Thu May  7 18:08:12 2026

@author: Dmytro
"""
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
import os
import nest_asyncio
import sys
sys.path.insert(1, os.getcwd() + '/tools/email')
sys.path.insert(1, os.getcwd() + '/tools/db')
from email_tool import send_email
from db_tool import search_citrus_trees, create_order

class TelegramAIBot:
    
    def __init__(self, auth_token: str, agent: AgentExecutor):
        self.app = Application.builder().token(auth_token).build()
        self.app.add_handler(MessageHandler(filters.TEXT, self.process_message))
        self.agent = agent
        self.conversation_history = {}
        
    def start_polling(self):
        print('About to start polling.')
        self.app.run_polling(1)
        print('Polling started.')

    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print('Message received. Begining processing...')
        message = update.message.text
        chat_id = update.message.chat.id
        print(self.conversation_history.get(chat_id, []))
        response = self.agent.invoke({
            "input" : message,
            "chat_history" : self.conversation_history.get(chat_id, [])
            }
            )['output'][0]['text']
        print('User\'s message:\n' + message)
        print('LLM\'s response:\n' + response)
        await update.message.reply_text(response)
        if(not (chat_id in self.conversation_history.keys())):
            self.conversation_history[chat_id] = [HumanMessage(message)]
        else:
            self.conversation_history[chat_id].append(HumanMessage(message))
        if(len(self.conversation_history[chat_id])>10):
            self.conversation_history[chat_id].pop(0)
            self.conversation_history[chat_id].pop(0)
        self.conversation_history[chat_id].append(AIMessage(response))

prompt = ChatPromptTemplate.from_messages([
    ("system", """Your name is Clementine and you are a Telegram chatbot, 
that assists customers of a citrus nursery with choosing and ordering a citrus 
tree. You are only going to be asked questions about citruses, if you are asked 
something different ignore such question by simply replying that you only answer 
questions about citruses. If you receive /start message greet the customer, 
introduce yourself and offer help, if you receive /help message say that you're 
here to assist with choosing a citrus tree and ask about which citrus tree a 
customer wants.Use  search_citrus_trees tool to search for citruses, that are 
for sale in a nursery. If customer wants to make an order, ask him for his name, 
email and citrus trees he wants to order, then create an order using create_order 
tool. After creating an order send an order confirmation email to a customer 
with his order id, using send_email tool. 
Try to keep your generated messages as short as possible, 
especially replies for /start and /help, remember - it's a chat in Telegram.
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")    ])

llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", 
                             api_key = os.environ['GOOGLE_GENAI_API_KEY'])
tools = [send_email, search_citrus_trees, create_order]
agent = create_tool_calling_agent(llm = llm, prompt = prompt, tools = tools)
agent_executor = AgentExecutor(agent = agent, tools = tools, verbose = True)
nest_asyncio.apply()
telegram_ai_bot = TelegramAIBot(os.environ['TELEGRAM_AUTH_TOKEN'], 
                                agent_executor)
telegram_ai_bot.start_polling()