#  0. Importing the necessary libraries
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

import os
from dotenv import load_dotenv, find_dotenv

# 0.1. Loading the environment variables
load_dotenv(find_dotenv())

# 1. Which LLM Provider to use? -> Google Chat Completions API Service
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model to use?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# 3. Creating the Agent
agent: Agent = Agent(name="ChefAssistant", model=llm_model, instructions="You are a prestigious Chef. You are given a list of ingredients and you need to create a recipe for a delicious dish. Keep your response short and to the point and be clear about steps for the recipe.")

print ("Enter your list of ingredients:")
ingredients = input()

# 4. Running the Agent
result = Runner.run_sync(starting_agent=agent, input=f"I have the following ingredients: {ingredients} \r\n Create a delicious recipe for me to cook using the mentioned ingredients.")

print("Chef says: ")
print(result.final_output)