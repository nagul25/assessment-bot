CURSOR PROJECT SPEC — STATIC FILE SEARCH + USER PDF→PNG + GPT-5 VISION

You are building enhancements for our current existing FastAPI backend system.
This system already accepts user-uploaded  PPT/PDFs, converts them into PNG images. 

There is a placeholder in process.py which needs to replaced with call to GPT-5 in Azure AI Foundry.

Now also extend it to support static standards-based assessments using Azure Assistants API.

🎯 Objective

Enhance the backend so it can:

Load static standard documents (EA principles, Cloud Principles, Experian General knowledge…) which are pdf files that will be added to the files folder

Upload these once to Azure Assistants API and store their file IDs

Create a permanent Assistant with:

GPT-5 model

file_search tool

the static standards file IDs

On every user request:

convert user PDF → PNGs (this already exists)

upload the PNGs to Azure (per request if required or if possible dont need to upload to Azure or use local copy)

send user prompt + PNGs to the assistant via a Thread

run the assistant

retrieve structured assessment

Combine:

static text standards (via file_search)

user images (via Vision)

This is exactly how ChatGPT "Custom GPTs" work — now replicated in your backend.

📁 Required Files to Generate or Modify
Create/update these modules inside backend/ or app/:

azure_assistant.py

Azure client initialization

Upload static standards

Create the assistant (one-time)

Upload user PNGs

Create thread + run

Poll for completion

standards_setup.py

Script to upload static files

Save file IDs to JSON or environment variables




README.md

Add instructions for standards setup

Add instructions for environment variables

🧠 System Behavior Specification
1. One-Time Setup: Upload Standard Files

Generate a script 

Should:

Read all files from static_standards/

Upload them to Azure:

client.files.create(file=open(f, "rb"), purpose="assistants")


Save returned file IDs in a JSON file:

standard_files.json:
{
  "files": ["file-abc123", "file-xyz456"]
}

2. Create Assistant (One-Time)

I have my own system prompt that describes the experian assessment bot behaviour

Use:

client.assistants.create(
    name="AssessmentAgent",
    instructions="Use these standards to evaluate user architectures…",
    model="gpt-5",
    tools=[{"type": "file_search"}],
    file_ids=[... static file IDs ...]
)


Store this assistant ID in config.

🖼️ 3. User Request Flow (FastAPI endpoint /assess)

For every user request:

(Already implemented)

✔ Receive uploaded PPT/PDF
✔ Convert PPT/PDF → PNGs

New steps to add:

Upload PNGs:

client.files.create(file=open("page0.png", "rb"), purpose="assistants")


Create a thread:

thread = client.threads.create(messages=[
    {
        "role": "user",
        "content": prompt,
        "attachments": [
            { "file_id": png_id }
        ]
    }
])


Run assistant:

run = client.threads.runs.create(
    assistant_id=ASSISTANT_ID,
    thread_id=thread.id
)


Poll for completion and get output:

messages = client.threads.messages.list(thread_id=thread.id)
answer = messages.data[0].content[0].text.value


Return answer to frontend.



⚙️ Environment Variables

Cursor should create .env.example 

✔️ Expectations From Cursor

Cursor should:

Modify or add all modules defined above

Respect the existing FastAPI structure

Not break your existing user-upload handling

Add Azure Assistants API integration cleanly

Provide clear docstrings and comments

Provide error handling and logging

Provide a README explaining setup

📝 Final Instruction to Cursor

“Build or update the backend according to the above complete specification.
Create all missing files, update existing ones, and ensure the full static file search + user PPT/PDF→PNG + GPT-5 assessment pipeline works end to end.”