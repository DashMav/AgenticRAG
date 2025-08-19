---
title: RAG AI-Agent
emoji: 💬
colorFrom: blue
colorTo: purple
colorGradient: true
sdk: docker
pinned: false
---

# RAG AI-Agent

RAG AI-Agent is a powerful Retrieval-Augmented Generation AI assistant that combines the capabilities of large language models with document-based knowledge retrieval. This application allows users to have conversational interactions with their documents by uploading files (PDF, TXT, DOCX), which are then semantically parsed, indexed, and made available for natural language queries.

The project consists of two main parts: a Python FastAPI backend and a React.js frontend.

## Features

*   **Document Processing**: Upload PDF, TXT, and DOCX documents to provide context for the AI.
*   **Natural Language Queries**: Ask questions in natural language, and the AI will use uploaded documents for accurate, context-aware responses.
*   **Agent Modes**:
    *   **Simple Mode**: Provides direct answers.
    *   **Agent Mode**: Offers advanced reasoning with detailed, step-by-step explanations of the AI's thought process, utilizing tools like a calculator and current time.
*   **Conversation Management**: Easily create new chats, rename them, or delete old ones using intuitive sidebar controls.
*   **Groq Integration**: Configured to use Groq API for fast inference.
*   **Developer Information**: Updated developer contact and social media links.

## Getting Started

Follow these instructions to set up and run the RAG AI-Agent locally.

### Prerequisites

*   Python 3.9+
*   Node.js and npm (or yarn)

### 1. Clone the Repository

```bash
git clone https://github.com/DashMav/AgenticRAG.git
cd AgenticRAG
```

**Note**: The project structure has been updated. The frontend is in `agent-frontend/` and the backend is in `backend/`.

### 2. Backend Setup (Python FastAPI)

1.  **Create a Virtual Environment and Install Dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # On Windows
    # source venv/bin/activate # On macOS/Linux
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables**:
    Create a `.env` file in the `backend/` directory and add your Groq API key:
    ```
    GROQ_API_KEY="your_groq_api_key_here"
    ```
    Replace `"your_groq_api_key_here"` with your actual Groq API key.

3.  **Run the Backend Server**:
    ```bash
    cd backend
    uvicorn app:app --reload
    ```
    The backend server will run on `http://127.0.0.1:8000`.

### 3. Frontend Setup (React.js with Vite)

1.  **Navigate to the Frontend Directory**:
    ```bash
    cd agent-frontend
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Set Environment Variables for Frontend**:
    Create a `.env` file in the `agent-frontend/` directory and set the API URL:
    ```
    VITE_API_URL=http://127.0.0.1:8000
    ```

4.  **Run the Frontend Development Server**:
    ```bash
    npm run dev
    ```
    The frontend application will typically run on `http://localhost:5174`.

### 4. Usage

1.  Open your web browser and navigate to `http://localhost:5174`.
2.  Start a new conversation, upload documents, or ask questions to the AI agent.
3.  Explore the "About Developer" section for more information about the creator.

## Deployment

This project is designed for a modern, serverless deployment using Vercel for the frontend and Hugging Face Spaces for the backend, with Pinecone for the vector database. This setup is completely free and does not require a credit card.

### Quick Deployment Guide

For detailed deployment instructions, please refer to our comprehensive deployment documentation:

- **[📋 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete step-by-step deployment instructions
- **[✅ DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Quick reference checklist for deployment
- **[🔧 ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Environment variable reference and configuration

### Maintenance and Updates

For ongoing maintenance and updates, see our comprehensive maintenance documentation:

- **[🔧 MAINTENANCE_SUMMARY.md](MAINTENANCE_SUMMARY.md)** - Quick reference for all maintenance procedures
- **[📖 MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md)** - Comprehensive maintenance and recovery procedures
- **[🔄 UPDATE_PROCEDURES.md](UPDATE_PROCEDURES.md)** - Step-by-step update procedures
- **[✅ MAINTENANCE_CHECKLIST.md](MAINTENANCE_CHECKLIST.md)** - Systematic maintenance checklists

### Deployment Overview

1. **Prerequisites**: Set up accounts for Pinecone, Hugging Face, Vercel, Groq, and OpenAI
2. **Pinecone Setup**: Create vector database index with 1536 dimensions
3. **Backend Deployment**: Deploy FastAPI app to Hugging Face Spaces using Docker
4. **Frontend Deployment**: Deploy React app to Vercel with API proxy configuration
5. **Verification**: Test all functionality end-to-end

### Quick Start

1. **Clone and prepare your repository**
2. **Set up Pinecone vector database** (free tier)
3. **Deploy backend to Hugging Face Spaces** with required API keys as secrets
4. **Deploy frontend to Vercel** with updated backend URL in `vercel.json`
5. **Verify deployment** using the provided checklists

For troubleshooting and detailed configuration, see the full deployment guide.

## Project Structure

```
RAG-AI-Agent/
├── .gitignore
├── LICENSE              # MIT License
├── README.md            # This file
├── agent-frontend/
│   ├── .gitignore
│   ├── .env             # Frontend environment variables (e.g., VITE_API_URL)
│   ├── index.html
│   ├── package.json     # Frontend dependencies and scripts
│   ├── vite.config.js
│   ├── public/
│   │   └── images/      # Static assets like AI and user icons
│   └── src/
│       ├── App.jsx      # Main React application component, routing
│       ├── AppClient.jsx # Axios client for API calls
│       ├── components/  # Reusable React components
│       ├── screens/     # Page-level React components (e.g., ChatPage, TwitterErrorPage)
│       └── ...
├── backend/
│   ├── .env                 # Backend environment variables (e.g., GROQ_API_KEY)
│   ├── agent.py             # Core AI agent logic, Groq integration
│   ├── app.py               # FastAPI backend application, API endpoints
│   ├── database.py          # Database models and utilities
│   ├── Dockerfile           # Dockerfile for backend deployment
│   ├── requirements.txt     # Python dependencies
│   ├── scripts/             # Backend scripts
│   ├── uploaded_files/      # Directory for uploaded files
│   ├── validate_deployment.py # Script to validate backend deployment
│   └── vector_database.py   # Vector database operations (ChromaDB)
└── images/              # Project images
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, collaborations, or new projects, feel free to reach out to Kiran S. Hegde at [kiran.s.hegde.05@gmail.com](mailto:kiran.s.hegde.05@gmail.com).
