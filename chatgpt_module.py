import os
from openai import OpenAI
import logging


### load .env file
from dotenv import load_dotenv
load_dotenv()

OPENAI_PROJECT=os.getenv('OPENAI_PROJECT')
OPENAI_ORGANIZATION=os.getenv('OPENAI_ORGANIZATION')
OPENAI_GPT_KEY=os.getenv('OPENAI_GPT_KEY')



def get_de_words_definition(prompt: str) -> str:
  client = OpenAI(
    organization=OPENAI_ORGANIZATION,
    project=OPENAI_PROJECT,
    api_key=OPENAI_GPT_KEY
  )

  ### ask chatgpt to teach me deutsch by explaining the given text 
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "gib mir die schwierigsten Wörter mit Definition in diesem Text im Textformat zum Posten im Telegramm. Bitte verwende auch Emojis, mindestens 10 Wörter: " + prompt}],
    max_tokens=180
    
  )
  result = response.choices[0].message.content
  ### return the response
  return(result)


### takes a promt as arguman and return the response as strung
def gpt_en_words_definition(prompt: str) -> str:
  client = OpenAI(
    organization=OPENAI_ORGANIZATION,
    project=OPENAI_PROJECT,
    api_key=OPENAI_GPT_KEY
  )

  ### ask chatgpt to teach me deutsch by explaining the given text 
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "gimme the hardest words with definition in this text in text format to post in telegram. please use emojies as well, at least 10 words : " + prompt}],
    max_tokens=180
    
  )
  result = response.choices[0].message.content
  ### return the response
  return(result)


### make simple dialog with chatgpt
def get_dialog(prompt: str) -> str:
  client = OpenAI(
    organization=OPENAI_ORGANIZATION,
    project=OPENAI_PROJECT,
    api_key=OPENAI_GPT_KEY
  )

  ### ask chatgpt to teach me deutsch by explaining the given text 
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Your name is Markus and as a german teacher fix the prompt if needed and response shortly in level A2:  " + prompt}],
    max_tokens=20
    
  )
  result = response.choices[0].message.content
  ### log number of token is used for debugging
  logging.debug(" number of tokens used: " + str(response.usage.total_tokens) )
  ### return the response
  return(result)

def get_de_words_definition(prompt: str) -> str:
  client = OpenAI(
    organization=OPENAI_ORGANIZATION,
    project=OPENAI_PROJECT,
    api_key=OPENAI_GPT_KEY
  )

  ### ask chatgpt to teach me deutsch by explaining the given text 
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "gib mir die deutschen Wortdefinitionen auf Englisch im Textformat zum Posten im Telegramm. Bitte verwende auch Emojis, mindestens 10 Wörter. Und eine englische Übersetzung des Textes am Ende. " + prompt}],
    max_tokens=180
    
  )
  logging.info("chat gpt api calls for de news api")
  result = response.choices[0].message.content
  ### return the response
  return(result)

