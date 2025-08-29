# main_code 


from openai import OpenAI 
import requests
import streamlit as st
import os
from webscrape import fetch_and_save

openai_api_key = st.secrets["OPENAI_API_KEY"]
serp_api_key = st.secrets["SERP_API_KEY"]

llm = OpenAI(api_key=openai_api_key)

OUTPUT_FILE = "output.txt"

# Function to determine if the query contains a URL using LLM
def extract_url_with_llm(query):
    """
    Uses LLM to determine if a query contains a URL.
    """
    response = llm.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an intelligent assistant. Your task is to determine if a user query requires extracting content from a URL or if the URL is just being referenced. If the user asks to summarize, analyze, or extract information from the URL, return only the URL. Otherwise, return 'None'."},
            {"role": "user", "content": query}
        ]
    )

    # extracted_url = response.choices[0].message.content.strip()
    # return extracted_url if extracted_url.lower() != "none" else None
    url = response.choices[0].message.content.strip()
    return url if url.startswith("http") else None  # Ensure a valid URL is returned

# Function to fetch data using web scraper
def fetch_from_web_scraper(url):
    """
    Fetches content from a URL using the web scraper and saves it to output.txt.
    Returns the scraped text content.
    """
    fetch_and_save(url, OUTPUT_FILE)

    # Read the scraped content
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            return file.read()
    
    return "No relevant information found."

# Function to check if LLM can answer the query
def ask_llm(query, context=""):
    """
    Queries the LLM with optional context.
    """
    response = llm.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an intelligent assistant. Carefully analyze the user's query and respond accurately based on your knowledge. If you are uncertain or lack sufficient information to provide a reliable answer, append 'I don't know for sure' at the end of your response. Only add this statement if you genuinely do not have a confident answer—do not include it if you are certain about the response."},
            {"role": "user", "content": f"{context} {query}"}
        ]
    )
    return response.choices[0].message.content

# Function to fetch data from SERP API if LLM cannot answer
def fetch_from_serp(query):

    search_url = f"https://serpapi.com/search.json?q={query}&api_key={serp_api_key}"
    
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get("organic_results", [])
        snippets = [f"{res['snippet']} (Source: {res['link']})" for res in results[:3]]
        return "\n".join(snippets) if snippets else "No relevant results found."
    return "Error fetching data from SERP API."

# Function to process user query
def process_query(query):
    """
    Processes the user query by first checking for a URL and scraping content if present.
    If no URL is found, it queries LLM, and if LLM is uncertain, it fetches results from SERP API.
    """
    url = extract_url_with_llm(query)
    
    if url:
        print("url being used:" + url)
    else:
        print("url not being used")

    if url:
        scraped_content = fetch_from_web_scraper(url)
        print("Scraped content from web:", scraped_content[:500])  # Log first 500 chars
        response = ask_llm(query, context=scraped_content)
    else:
        llm_response = ask_llm(query)
        print("LLM response:", llm_response)
        
        if "I don't know" in llm_response or "I'm not sure" in llm_response or "I don't know for sure" in llm_response:
            serp_result = fetch_from_serp(query)
            response = ask_llm(query, context=serp_result) + f"\n\nSources: {serp_result}"
        else:
            response = llm_response

    return {"query": query, "response": response}

# Streamlit Frontend
st.title("Conversational AI Chatbot")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

query = st.chat_input("Ask me anything:")
if query:
    response_data = process_query(query)
    st.session_state.conversation_history.append(response_data)

# Display chat history
for chat in st.session_state.conversation_history:
    st.write(f"**You:** {chat['query']}")
    st.write(f"**Bot:** {chat['response']}")




# few limitations
# 1. in the first funciton - the llm might hallucinate while determining the url
# 2. the scraper cannot work for websites with captcha, or websites that are not static
# 3. the scraper might not work for websites that are not in english
# 4. if the query requires to fetch data from 2 urls, then code has to be put in loop.
# 5. 
