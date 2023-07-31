import os
import csv
# import requests
import pandas as pd
from getpass import getpass
from langchain import HuggingFaceHub
from langchain.vectorstores import FAISS
from langchain.chains import ConversationChain
from langchain.document_loaders import TextLoader
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.question_answering import load_qa_chain
# from langchain.document_loaders import WebBaseLoader


# HUGGINGFACEHUB_API_TOKEN = getpass()
HUGGINGFACEHUB_API_TOKEN = 'HUGGINGFACEHUB_API_TOKEN'
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

# FOR LARGE DATASET UNCOMMENT THIS

# import requests
# import xml.etree.ElementTree as ET

# url = "https://www.nu.edu.pk/sitemap.xml"

# # Fetch the XML data from the URL
# response = requests.get(url)
# data = response.text

# # Parse the XML data
# root = ET.fromstring(data)

# Extract the <loc> part and append it to an array
# urls_array = []
# for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
#     urls_array.append(url.text)

# print(urls_array)

# import csv
# from langchain.document_loaders import WebBaseLoader

# urls = list(urls_array)

# all_data = []

# for url in urls:
#     try:
#         loader = WebBaseLoader(url)
#         data = loader.load()
#         all_data.extend(data)
#     except Exception as e:
#         print(f"Failed to scrape {url}: {e}")

# print(type(all_data),len(all_data))
# Write the data to a CSV file
# output_file = "Dataset.csv"

# with open(output_file, mode="w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f)
#     writer.writerow(["HTML"])

#     for doc in all_data:
#         html = str(doc)

#         writer.writerow([html])

# print(f"Data has been saved to {output_file}.")

# Small Dataset
urls = ['https://www.nu.edu.pk/Admissions/Schedule', 'https://www.nu.edu.pk/Admissions/HowToApply', 'https://www.nu.edu.pk/Admissions/EligibilityCriteria',
        'https://www.nu.edu.pk/Admissions/Scholarship','https://www.nu.edu.pk/Admissions/TestPattern', 'https://www.nu.edu.pk/Admissions/FeeStructure',
        'https://www.nu.edu.pk/Admissions/Prospectus']

# Initialize an empty list to store the loaded data from each page
all_data = []

for url in urls:
    try:
        loader = WebBaseLoader(url)
        data = loader.load()
        all_data.extend(data)  # Extend the list instead of appending
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

# Write the data to a CSV file
output_file = "Data.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["HTML"])

    for doc in all_data:  # Iterate over each document in the list
        html = str(doc)  # Convert the Document object to its textual representation

        writer.writerow([html])

print(f"Data has been saved to {output_file}.")



loader = TextLoader('./Data.csv')
documents = loader.load()
# print(documents)

import re
def clean_page_content(page_content):
    # Remove any leading or trailing whitespace and newlines
    cleaned_page_content = page_content.strip()
    # Remove extra newlines and whitespaces within the content
    cleaned_page_content = re.sub(r'\n+', '\n', cleaned_page_content)
    # Remove any extra spaces at the beginning of each line
    cleaned_page_content = re.sub(r'^\s+', '', cleaned_page_content, flags=re.MULTILINE)
    # Remove "Home" and "Contact" from the content
    cleaned_page_content = re.sub(r'\b(?:Home|Contact)\b', '', cleaned_page_content)
    return cleaned_page_content

def clean_dataset(data):
    # Initialize an empty list to store the cleaned page content for each document
    cleaned_data = []

    # Iterate over each document in the dataset
    for doc in data:
        # Get the page_content from the document
        page_content = doc.page_content

        # Clean the page_content using the clean_page_content function
        cleaned_page_content = clean_page_content(page_content)

        # Append the cleaned page_content to the cleaned_data list
        cleaned_data.append(cleaned_page_content)

    return cleaned_data


cleaned_data = clean_dataset(all_data)

# cleaned_data

import textwrap

def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split('\n')

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = '\n'.join(wrapped_lines)

    return wrapped_text

# print(wrap_text_preserve_newlines(str(cleaned_data[0])))


text_splitter = CharacterTextSplitter(chunk_size=1300, chunk_overlap=10)
docs = text_splitter.split_documents(all_data)
print(len(docs))
# print(docs[0])

embeddings = HuggingFaceEmbeddings()
db = FAISS.from_documents(docs, embeddings)

# query = "Is bank loan avaliable?"
# docs = db.similarity_search(query)
# print(wrap_text_preserve_newlines(str(docs[0].page_content)))


# llm=HuggingFaceHub(repo_id="google/flan-t5-small", model_kwargs={"temperature":0, "max_length":512})
llm=HuggingFaceHub(repo_id="tiiuae/falcon-7b", model_kwargs={"temperature":0.1, "max_length":512})
chain = load_qa_chain(llm, chain_type="stuff")
print(chain)
print(llm)
# query = "What is your Admission fee?"
# docs = db.similarity_search(query)
# R = chain.run(input_documents=docs, question=query)
# print(wrap_text_preserve_newlines(str(R)))

query = "State your Fee Refund Policy?"
docs = db.similarity_search(query)
Res = chain.run(input_documents=docs, question=query)
# print(wrap_text_preserve_newlines(str(Res)))
# Res



# Create a ConversationBufferWindowMemory to store the conversation history
mem = ConversationBufferWindowMemory(k=1000)
conversation = ConversationChain(llm=llm, verbose=True, memory=mem)

# Function to save student details to a text file
def save_student_details(name, mobile_number, degree):
    with open("student_details.txt", "w") as file:
        file.write(f"Name: {name}\n")
        file.write(f"Mobile Number: {mobile_number}\n")
        file.write(f"Degree: {degree}\n")

# Function to get similar documents using similarity search
def get_similar_documents(query):
    # Replace this with the actual implementation of similarity_search using your database (db)
    docs = db.similarity_search(query)
    return docs

def get_chatbot_response(question, docs):
    # Get the conversation history from the conversation object
    conversation_history = []
    for item in conversation.memory:
        if "input" in item:
            conversation_history.append(f"You: {item['input']}")
        if "response" in item:
            conversation_history.append(f"Chatbot: {item['response']['message']}")
    response = chain.run(input_documents=docs, question=question)
    # Return the response message and conversation history as a dictionary
    return {"message": response, "conversation": conversation_history}


# def get_chatbot_response(question, docs):
#     # # Add the 'input' key to the input_documents dictionary
#     # input_documents = {'input': question}
#     # input_documents.update(docs)
#     # response = conversation.predict(input_documents=input_documents)
    
#     response = chain.run(input_documents=docs, question=question)
#     return response

# Conversation with the chatbot
def run_conversation():
    print("Chatbot: Hi there! I'm an AI. What's your name?")
    name = input("You: ")

    print("Chatbot: Nice to meet you, " + name + "! What's your mobile number?")
    mobile_number = input("You: ")

    print("Chatbot: Great! Which degree do you want to apply for?")
    degree = input("You: ")

    save_student_details(name, mobile_number, degree)
    print("Chatbot: Thank you for providing your details. How can I help you?")

    # Proper conversation loop
    # conversation_history = []  # Initialize conversation history list
    while True:
        user_input = input("You: ").strip().lower()
        # conversation_history.append(f"You: {user_input}")

        if user_input == 'q':
            print("Chatbot: Goodbye! Have a great day!")
            break

        similar = get_similar_documents(user_input)
        response = get_chatbot_response(user_input, similar)
        # conversation_history.append(f"Chatbot: {response}")
        print("Chatbot: ", response)

# Run the conversation
# run_conversation()