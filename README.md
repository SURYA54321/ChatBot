# 🤖 AI RAG Chatbot

An AI-powered chatbot built with **React.js, Django, LangChain, Groq, and Retrieval-Augmented Generation (RAG)**.

The chatbot supports normal conversations, multiple chat sessions, document-based question answering, chat history, JWT authentication, PDF processing, OCR for image-based PDFs, and streaming AI responses.

## 🚀 Live Demo

**Frontend:**
https://chat-bot-five-lilac.vercel.app

**Backend:**
https://chatbot-fguf.onrender.com

**Health Check:**
https://chatbot-fguf.onrender.com/api/health/

---

## ✨ Features

* 🔐 User registration and JWT authentication
* 🔑 Access and refresh token authentication
* 💬 Normal AI conversations
* 🗂️ Multiple chat conversations
* 📝 Chat history and recent conversation context
* 📄 Document upload
* 📚 Document-based RAG
* 🎯 Conversation-scoped document retrieval
* 🔍 Semantic similarity search
* 🧠 Hugging Face embeddings
* 🗃️ SQLite-based vector storage
* 📊 NumPy cosine similarity
* 📑 PDF text extraction
* 🖼️ OCR support for image-based PDFs
* ⚡ Streaming AI responses
* 📚 Source information for RAG responses
* 🛡️ Relevance checking to avoid unrelated document retrieval
* 🐳 Docker support
* ☁️ Render backend deployment
* ▲ Vercel frontend deployment
* ❤️ Health-check endpoint for monitoring

---

## 🧠 RAG Implementation

This project implements a lightweight RAG pipeline without using a dedicated vector database.

### RAG Flow

```text
User uploads document
        ↓
Document stored
        ↓
Text extraction
        ↓
OCR fallback for image-based PDFs
        ↓
Text chunking
        ↓
Generate embeddings
        ↓
Store chunks + embeddings in SQLite
        ↓
User asks a question
        ↓
Generate query embedding
        ↓
Search only current conversation's documents
        ↓
Calculate cosine similarity
        ↓
Check relevance
        ↓
Retrieve relevant chunks
        ↓
Send context + question to LLM
        ↓
Generate answer
        ↓
Return answer + sources
```

---

## 🎯 Conversation-Scoped RAG

One important part of the project is that uploaded documents belong to a specific conversation.

For example:

```text
Chat 1
 ├── resume.pdf
 └── User questions

Chat 2
 ├── notes.pdf
 └── User questions
```

When the user asks a question in **Chat 1**, the retrieval system only searches documents belonging to **Chat 1**.

It does not search documents uploaded in other conversations.

This prevents unrelated documents from being included in the response.

---

## 💬 Normal Chat vs RAG

The chatbot does not automatically use document retrieval for every message.

Example:

```text
No document + "Hi"
        ↓
Normal Chat
```

```text
Document uploaded + "How are you?"
        ↓
Normal Chat
```

```text
Document uploaded + "What does the document say about cancellation?"
        ↓
RAG
```

```text
Document uploaded + unrelated question
        ↓
Relevance check
        ↓
Normal Chat
```

Common obvious conversational messages such as:

```text
Hi
Hello
Hey
How are you?
Good morning
Thanks
Bye
```

are handled directly as normal chat.

Document-level questions such as:

```text
Explain the document
Summarize the document
What is this document about?
```

are allowed to use the uploaded document even when their semantic similarity score is low.

---

## 📄 PDF Processing

The application supports normal text-based PDFs as well as image-based PDFs.

### Normal PDF

```text
PDF
 ↓
PyMuPDF
 ↓
Extract text
 ↓
Chunk text
```

### Image-based PDF

```text
PDF
 ↓
PyMuPDF
 ↓
Text not usable
 ↓
Render page as image
 ↓
Tesseract OCR
 ↓
Extract text
 ↓
Chunk text
```

This allows the chatbot to process scanned/image-based documents as well.

---

## 🧠 Embeddings

The project uses:

**Hugging Face**

Model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The document chunks are converted into numerical vectors called **embeddings**.

The user's question is also converted into an embedding.

The system then compares them using cosine similarity.

---

## 🔍 Similarity Search

Instead of using Chroma, Pinecone, or another dedicated vector database, this project uses:

```text
SQLite
+
Django ORM
+
JSONField
+
NumPy
```

Document embeddings are stored in SQLite as JSON data.

When a question is asked:

```text
Question
   ↓
Query embedding
   ↓
Compare with stored embeddings
   ↓
Cosine similarity
   ↓
Sort by similarity
   ↓
Retrieve relevant chunks
```

This keeps the project simple and suitable for an interview/demo application.

---

## 🤖 LLM

The project uses the **Groq API** through LangChain.

LangChain is responsible for integrating the application with the LLM and managing the RAG pipeline.

The retrieved document chunks are included as context before generating the final answer.

---

## ⚡ Streaming Responses

The chatbot supports streaming responses.

Instead of waiting for the complete AI response:

```text
User
 ↓
Backend
 ↓
LLM
 ↓
Token
Token
Token
Token
...
 ↓
Frontend
```

The frontend displays the response as it is generated.

The backend uses Django's:

```python
StreamingHttpResponse
```

and the React frontend reads the streamed response using the Fetch API.

---

## 🔐 Authentication

The application uses JWT authentication.

Authentication flow:

```text
Register
   ↓
Login
   ↓
Access Token + Refresh Token
   ↓
Access Token used for API requests
   ↓
Access Token expires
   ↓
Refresh Token
   ↓
New Access Token
```

Protected chat and document APIs require authentication.

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* Vite
* Axios
* Fetch API
* CSS

### Backend

* Python
* Django
* Django REST Framework

### AI / RAG

* LangChain
* Groq API
* Hugging Face Embeddings
* `all-MiniLM-L6-v2`
* NumPy
* Cosine Similarity

### Document Processing

* PyMuPDF
* Tesseract OCR
* pytesseract
* Pillow

### Database

* SQLite
* Django ORM
* JSONField

### Authentication

* JWT
* Access Tokens
* Refresh Tokens

### Deployment

* Docker
* Gunicorn
* Render
* Vercel
* WhiteNoise

### Monitoring

* Health-check endpoint
* Better Stack monitoring

---

## 📁 Project Structure

```text
ChatBot/
│
├── backend/
│   │
│   ├── chat/
│   ├── conversations/
│   ├── documents/
│   ├── users/
│   ├── rag/
│   │   ├── embeddings/
│   │   ├── loaders/
│   │   ├── retrievers/
│   │   ├── vectorstore/
│   │   ├── prompts/
│   │   ├── ingestion.py
│   │   └── pipeline.py
│   │
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/SURYA54321/ChatBot.git
cd ChatBot
```

---

# Backend Setup

### 2. Move into backend

```bash
cd backend
```

### 3. Create virtual environment

```bash
python -m venv venv
```

### 4. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file inside the backend directory.

Example:

```env
SECRET_KEY=your-secret-key

DEBUG=True

GROQ_API_KEY=your-groq-api-key

HUGGINGFACEHUB_API_TOKEN=your-huggingface-token

ALLOWED_HOSTS=127.0.0.1,localhost

CORS_ALLOWED_ORIGINS=http://localhost:5173

SQLITE_PATH=db.sqlite3

MEDIA_ROOT=media
```

For Windows OCR, configure Tesseract if necessary:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 7. Run migrations

```bash
python manage.py migrate
```

### 8. Start Django

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

---

# Frontend Setup

Open another terminal.

### 9. Move into frontend

```bash
cd frontend
```

### 10. Install dependencies

```bash
npm install
```

### 11. Configure backend URL

Create:

```text
.env
```

Example:

```env
VITE_BACKEND_URL=http://127.0.0.1:8000/api
```

### 12. Start React

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 🔑 Required API Keys

The application requires:

| Variable                   | Purpose                                 |
| -------------------------- | --------------------------------------- |
| `GROQ_API_KEY`             | Access to the LLM                       |
| `HUGGINGFACEHUB_API_TOKEN` | Generate document/query embeddings      |
| `SECRET_KEY`               | Django security                         |
| `CORS_ALLOWED_ORIGINS`     | Frontend/backend communication          |
| `ALLOWED_HOSTS`            | Django allowed hosts                    |
| `SQLITE_PATH`              | SQLite database path                    |
| `MEDIA_ROOT`               | Uploaded document storage               |
| `TESSERACT_CMD`            | Tesseract executable path when required |

**Never commit real API keys or `.env` files to GitHub.**

---

## 🐳 Docker

The backend includes Docker support.

Build the image:

```bash
docker build -t chatbot-backend .
```

Run the container:

```bash
docker run -p 10000:10000 chatbot-backend
```

The Docker image includes:

```text
Python
Django
Gunicorn
Tesseract OCR
Project dependencies
```

---

## ☁️ Deployment

### Backend

The Django backend is deployed using:

```text
Docker
   ↓
Render
   ↓
Gunicorn
   ↓
Django
```

### Frontend

The React frontend is deployed using:

```text
Vite React App
       ↓
     Vercel
```

---

## ❤️ Health Check

The backend provides:

```text
/api/health/
```

Example response:

```json
{
    "status": "ok"
}
```

This endpoint can be used by monitoring services to check whether the backend is running.

---

## 🔄 Complete Application Flow

```text
                    ┌───────────────┐
                    │     React     │
                    │    Frontend   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Django REST   │
                    │     API       │
                    └───────┬───────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          ┌─────────────┐       ┌─────────────┐
          │   SQLite    │       │ RAG Pipeline│
          │  Database   │       │             │
          └─────────────┘       └──────┬──────┘
                                       │
                          ┌────────────┼────────────┐
                          │            │            │
                          ▼            ▼            ▼
                     Embeddings    Retrieval     Relevance
                          │            │            │
                          └────────────┼────────────┘
                                       │
                                       ▼
                                  ┌──────────┐
                                  │  Groq    │
                                  │   LLM    │
                                  └────┬─────┘
                                       │
                                       ▼
                                  AI Response
                                       │
                                       ▼
                                    React
```

---

## 🎯 Why SQLite for Vector Storage?

This project is designed as an **interview/demo project**, so a lightweight architecture was preferred.

Instead of using a dedicated vector database, embeddings are stored in SQLite and compared using NumPy cosine similarity.

This keeps the implementation simple while demonstrating the core concepts of:

* Embeddings
* Vector similarity
* Retrieval
* Context injection
* RAG
* Document-scoped search

For a large-scale production system, a dedicated vector database could be considered.

---

## 🚧 Future Improvements

Possible future improvements include:

* Background document processing
* Better OCR preprocessing
* More document formats
* Improved chunking strategies
* Reranking models
* Dedicated vector database for large-scale applications
* Cloud object storage for uploaded files
* More advanced conversation memory
* Automated testing
* CI/CD pipeline

---

## 👨‍💻 Author

**Surya**

GitHub:

https://github.com/SURYA54321

---

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐.
