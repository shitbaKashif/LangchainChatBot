from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from databases import Database
from Chat import get_similar_documents, get_chatbot_response, conversation

# Create a FASTAPI app
app = FastAPI()

# Templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# MySQL database configurations
DATABASE_URL = "mysql+mysqlconnector://username:password@localhost/db_name"
# Replace 'username', 'password', 'localhost', and 'db_name' with your MySQL credentials and database name

# Create a database instance
database = Database(DATABASE_URL)
print(type(conversation))
# Startup event to connect to the database
@app.on_event("startup")
async def startup_db():
    await database.connect()
    # Create the user_questions table if it doesn't exist
    query = """
    CREATE TABLE IF NOT EXISTS user_questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(255),
        question VARCHAR(1000),
        answer VARCHAR(1000)
    )
    """
    await database.execute(query)

# Shutdown event to disconnect from the database
@app.on_event("shutdown")
async def shutdown_db():
    await database.disconnect()

# Pydantic model for request body
class QuestionRequest(BaseModel):
    user_id: int
    question: str

# Pydantic model for response body
class AnswerResponse(BaseModel):
    answer: str
    chat: list

# # POST endpoint to get the answer based on user question
# @app.post("/get_answer/", response_model=AnswerResponse)
# async def get_answer(question_request: QuestionRequest):
#     # Check if the user_id and question are provided
#     if not question_request.user_id or not question_request.question:
#         raise HTTPException(status_code=400, detail="Userid and question must be provided.")

#     # Perform some processing to get the answer based on the user's question (You can use your LLM model here)
#     # For this example, let's use the chatbot response from 'practice.py'
#     similar = get_similar_documents(question_request.question)
#     answer_response = get_chatbot_response(question_request.question, similar)
#     answer = answer_response

#     # Save the user question and answer in the MySQL database
#     query = "INSERT INTO user_questions (user_id, question, answer) VALUES (:user_id, :question, :answer)"
#     values = {"user_id": question_request.user_id, "question": question_request.question, "answer": answer}
#     await database.execute(query=query, values=values)

#     # Get chat history from conversation memory (practice.py)
#     chat_history = []
#     conversation = get_chatbot_response.conversation  # Access the conversation history
#     for item in conversation.memory:
#         if "input" in item:
#             chat_history.append(f"You: {item['input']}")
#         if "response" in item:
#             chat_history.append(f"Chatbot: {item['response']['message']}")

#     # Return the answer and chat history
#     return {"answer": answer, "chat": chat_history}

# POST endpoint to get the answer based on user question
# @app.post("/get_answer/", response_model=AnswerResponse)
# async def get_answer(question_request: QuestionRequest):
#     # Check if the user_id and question are provided
#     if not question_request.user_id or not question_request.question:
#         raise HTTPException(status_code=400, detail="Userid and question must be provided.")

#     # Perform some processing to get the answer based on the user's question (You can use your LLM model here)
#     similar = get_similar_documents(question_request.question)
#     answer_response = get_chatbot_response(question_request.question, similar)
#     answer = answer_response

#     # Save the user question and answer in the MySQL database using parameterized query
#     query = "INSERT INTO user_questions (user_id, question, answer) VALUES (%s, %s, %s)"
#     values = (question_request.user_id, question_request.question, answer)
#     try:
#         await database.execute(query=query, values=values)
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to save data to the database.")

#     # Add the user question and chatbot response to the conversation history
#     conversation.memory.append({"input": question_request.question, "response": {"message": answer_response}})

#     # Get chat history from the conversation memory
#     chat_history = []
#     for item in conversation.memory:
#         if "input" in item:
#             chat_history.append(f"You: {item['input']}")
#         if "response" in item:
#             chat_history.append(f"Chatbot: {item['response']['message']}")

#     # Return the answer and chat history
#     return {"answer": answer, "chat": chat_history}

# POST endpoint to get the answer based on user question
@app.post("/get_answer/", response_model=AnswerResponse)
async def get_answer(question_request: QuestionRequest):
    # Check if the user_id and question are provided
    if not question_request.user_id or not question_request.question:
        raise HTTPException(status_code=400, detail="Userid and question must be provided.")

    # Perform some processing to get the answer based on the user's question (You can use your LLM model here)
    similar = get_similar_documents(question_request.question)
    answer_response = get_chatbot_response(question_request.question, similar)
    answer = answer_response['message']

    # Save the user question and answer in the MySQL database using parameterized query
    query = "INSERT INTO user_questions (user_id, question, answer) VALUES (:user_id, :question, :answer)"
    values = {"user_id": question_request.user_id, "question": question_request.question, "answer": answer}
    try:
        await database.execute(query=query, values=values)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to save data to the database.")

    # Add the user question and chatbot response to the conversation history
    # conversation.memory.append({"input": question_request.question, "response": {"message": answer_response}})
    # conversation.memory.add_item({"input": question_request.question, "response": {"message": answer_response}})
    # Get chat history from the conversation memory
    chat_history = []
    for item in conversation.memory:
        if "input" in item:
            chat_history.append(f"You: {item['input']}")
        if "response" in item:
            chat_history.append(f"Chatbot: {item['response']['message']}")

    # Return the answer and chat history
    return {"answer": answer, "chat": chat_history}

# GET endpoint to display the webpage for user input and chat display
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
