# Backend/Prod/api.py

from fastapi import FastAPI, Path, Body
from pydantic import BaseModel
from typing import List, Dict
from sullivan_chatbot import get_organes_for_corps, chat

app = FastAPI()

class MessageRequest(BaseModel):
    message: str
    context: Dict = {}

@app.get("/sullivan/corps/{corps_id}/organes")
async def get_organes(
    corps_id: str, 
    screen_plan: Path = "output/studio/screen_plan.json"
):
    """
    Get the list of organs for a given corps ID from the screen plan.

    Args:
    corps_id (str): ID of the corps.
    screen_plan (Path): Path to the screen plan JSON file.

    Returns:
    Dict: Dictionary containing the corps ID and the list of organs.
    """
    organs = get_organes_for_corps(corps_id, screen_plan)
    return {"corps_id": corps_id, "organes": organs}

@app.post("/sullivan/chatbot")
async def chatbot(request: MessageRequest):
    """
    Chat with the user and return a response.

    Args:
    request (MessageRequest): Request containing the user message and context.

    Returns:
    Dict: Dictionary containing the reply from the chatbot.
    """
    response = await chat(request.message, request.context)
    return {"reply": response}

# Backend/Prod/sullivan/builder/corps1_chatbot_page.py

from fastapi import FastAPI
import json
from typing import List, Dict
from pathlib import Path
import os

def generate_corps1_chatbot_html(base_url: str, screen_plan_path: Path) -> str:
    """
    Generate an HTML page containing a section for corps 1 and a chatbot widget.

    Args:
    base_url (str): Base URL for the API.
    screen_plan_path (Path): Path to the screen plan JSON file.

    Returns:
    str: HTML page as a string.
    """
    html = """
    <html>
    <head>
    <title>Corps 1 Chatbot</title>
    <style>
    body {
        font-family: monospace;
    }
    .chatbot-widget {
        position: fixed;
        bottom: 0;
        right: 0;
        z-index: 10;
        border: 1px solid black;
        padding: 10px;
        width: 300px;
        height: 200px;
    }
    </style>
    </head>
    <body>
    <h1>Corps 1</h1>
    <div id="corps1-organes">
    """
    try:
        with open(screen_plan_path, 'r') as f:
            screen_plan = json.load(f)
        for corps in screen_plan:
            if corps['id'] == '1':
                organs = corps.get('organs', [])
                html += "<p>Organes: " + ", ".join([organe['name'] for organe in organs]) + "</p>"
                break
    except FileNotFoundError:
        html += "<p>Screen plan file not found.</p>"
    except json.JSONDecodeError:
        html += "<p>Invalid JSON in screen plan file.</p>"
    html += """
    </div>
    <div class="chatbot-widget">
    <textarea id="message" placeholder="Type a message..."></textarea>
    <button id="send-button">Envoyer</button>
    <div id="responses"></div>
    <script>
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send-button');
    const responsesDiv = document.getElementById('responses');
    sendButton.addEventListener('click', async () => {
        const message = messageInput.value;
        const response = await fetch('{}/sullivan/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message, context: {} })
        });
        const reply = await response.json();
        responsesDiv.innerHTML += '<p>' + reply.reply + '</p>';
        messageInput.value = '';
    });
    </script>
    </div>
    </body>
    </html>
    """
    return html

def build_corps1_chatbot_page(screen_plan_path: Path, output_path: Path, base_url: str):
    """
    Build the corps 1 chatbot page and save it to the output path.

    Args:
    screen_plan_path (Path): Path to the screen plan JSON file.
    output_path (Path): Path to the output HTML file.
    base_url (str): Base URL for the API.
    """
    html = generate_corps1_chatbot_html(base_url, screen_plan_path)
    with open(output_path, 'w') as f:
        f.write(html)

# Usage
if __name__ == "__main__":
    screen_plan_path = Path("output/studio/screen_plan.json")
    output_path = Path("output/studio/studio_corps1_chatbot.html")
    base_url = "http://localhost:8000"
    build_corps1_chatbot_page(screen_plan_path, output_path, base_url)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import requests
import json

app = FastAPI()

# Define the base directory for addendum files
ADDENDUM_DIR = "output/studio/addendum"

# Create the addendum directory if it doesn't exist
if not os.path.exists(ADDENDUM_DIR):
    os.makedirs(ADDENDUM_DIR)

class Task(BaseModel):
    corps_id: str
    addendum_path: Optional[str]
    context: Optional[Dict]

class ValidateAndNextRequest(BaseModel):
    state: Optional[Dict]

# Define a function to generate questions using Gemini
def generate_questions(corps_id: str, addendum_path: Optional[str], context: Dict) -> List[str]:
    if addendum_path:
        # Construct the prompt for Gemini
        prompt = f"Contexte : écran corps {corps_id}, addendum graphique fourni (chemin ou description). Génère 1 à 3 questions courtes pour clarifier l'intention de l'utilisateur (ex. Ce bloc doit-il être une liste ou un formulaire ?). Retourne uniquement les questions, une par ligne."
        
        # Call Gemini with the prompt
        response = requests.post("https://api.gemini.com/v1/generate", json={"prompt": prompt})
        
        # Parse the response as a list of strings
        questions = response.json()["response"].split("\n")
        
        return questions
    else:
        return []

# Define the endpoint to upload an addendum file
@app.post("/sullivan/addendum/upload")
async def upload_addendum(file: UploadFile = File(...)):
    # Get the file name and extension
    filename = file.filename
    file_extension = filename.split(".")[-1]
    
    # Generate a unique file name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"addendum_{timestamp}.{file_extension}"
    
    # Save the file to the addendum directory
    file_path = os.path.join(ADDENDUM_DIR, new_filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Return the file path and name
    return {"path": file_path, "filename": new_filename}

# Define the endpoint to generate questions for the chatbot
@app.post("/sullivan/chatbot/questions")
async def generate_chatbot_questions(task: Task):
    questions = generate_questions(task.corps_id, task.addendum_path, task.context)
    return {"questions": questions}

# Define the endpoint to validate and get the next corps
@app.post("/sullivan/corps/{corps_id}/validate-and-next")
async def validate_and_next(corps_id: str, request: Optional[ValidateAndNextRequest] = None):
    # Load the screen plan from the JSON file
    with open("output/studio/screen_plan.json", "r") as f:
        screen_plan = json.load(f)
    
    # Find the next corps in the screen plan
    next_corps_id = None
    next_label = None
    organes = []
    for corps in screen_plan:
        if corps["id"] == corps_id:
            # Check if there is a next corps
            if corps["next_corps_id"]:
                next_corps_id = corps["next_corps_id"]
                next_label = corps["next_label"]
                organes = corps["organes"]
            break
    
    # Return the next corps information or a 404 error if not found
    if next_corps_id:
        return {"next_corps_id": next_corps_id, "next_label": next_label, "organes": organes}
    else:
        raise HTTPException(status_code=404, detail="No next corps found")

# Define the endpoint to serve the HTML page
@app.get("/sullivan/corps/{corps_id}")
async def serve_corps_page(corps_id: str):
    with open("output/studio/studio_corps_chatbot.html", "r") as f:
        html = f.read()
    
    # Replace the placeholders with the actual values
    html = html.replace("{{ corps_id }}", corps_id)
    
    return HTMLResponse(content=html, media_type="text/html")

# Define the static files directory
app.mount("/static", StaticFiles(directory="output/studio/static"), name="static")

# Generate the HTML page
with open("output/studio/studio_corps_chatbot.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Corps {{ corps_id }}</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <h1>Corps {{ corps_id }}</h1>
        <form id="addendum-form">
            <input type="file" id="addendum-file" accept="image/*">
            <button id="addendum-button">Ajouter addendum</button>
        </form>
        <div id="questions-div"></div>
        <button id="next-button">Passer à l'écran suivant</button>
        
        <script>
            const addendumForm = document.getElementById("addendum-form");
            const addendumButton = document.getElementById("addendum-button");
            const questionsDiv = document.getElementById("questions-div");
            const nextButton = document.getElementById("next-button");
            
            addendumButton.addEventListener("click", async (e) => {
                e.preventDefault();
                const file = document.getElementById("addendum-file").files[0];
                const formData = new FormData();
                formData.append("file", file);
                
                const response = await fetch("/sullivan/addendum/upload", {
                    method: "POST",
                    body: formData,
                });
                
                const data = await response.json();
                console.log(data);
                
                const questionsResponse = await fetch("/sullivan/chatbot/questions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        corps_id: "{{ corps_id }}",
                        addendum_path: data.path,
                        context: {},
                    }),
                });
                
                const questionsData = await questionsResponse.json();
                console.log(questionsData);
                
                questionsDiv.innerHTML = "";
                questionsData.questions.forEach((question) => {
                    const questionElement = document.createElement("p");
                    questionElement.textContent = question;
                    questionsDiv.appendChild(questionElement);
                    
                    const answerElement = document.createElement("textarea");
                    questionsDiv.appendChild(answerElement);
                });
            });
            
            nextButton.addEventListener("click", async (e) => {
                e.preventDefault();
                const response = await fetch("/sullivan/corps/{{ corps_id }}/validate-and-next", {
                    method: "POST",
                });
                
                const data = await response.json();
                console.log(data);
                
                // Update the page with the next corps information
                document.getElementById("corps-id").textContent = data.next_corps_id;
                document.getElementById("corps-label").textContent = data.next_label;
                document.getElementById("organes").innerHTML = "";
                data.organes.forEach((organe) => {
                    const organeElement = document.createElement("p");
                    organeElement.textContent = organe;
                    document.getElementById("organes").appendChild(organeElement);
                });
            });
        </script>
    </body>
    </html>
    """)