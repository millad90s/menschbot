import os
from openai import OpenAI

### load .env file
from dotenv import load_dotenv
load_dotenv()

OPENAI_PROJECT=os.getenv('OPENAI_PROJECT')
OPENAI_ORGANIZATION=os.getenv('OPENAI_ORGANIZATION')
OPENAI_GPT_KEY=os.getenv('OPENAI_GPT_KEY')


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