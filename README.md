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

### 2. Backend Setup (Python FastAPI)

1.  **Create a Virtual Environment and Install Dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # On Windows
    # source venv/bin/activate # On macOS/Linux
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables**:
    Create a `.env` file in the root directory of the project (`RAG-AI-Agent/`) and add your Groq API key:
    ```
    GROQ_API_KEY="your_groq_api_key_here"
    ```
    Replace `"your_groq_api_key_here"` with your actual Groq API key.

3.  **Run the Backend Server**:
    ```bash
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

This project is designed to be deployed with a separate frontend and backend. We recommend using Vercel for the frontend and Render for the backend, both of which offer generous free tiers.

### 1. Deploying the Backend to Render

1.  **Push your code to a GitHub repository.**
2.  Go to the [Render dashboard](https://dashboard.render.com/) and create a new "Blueprint" service.
3.  Connect your GitHub repository. Render will automatically detect the `render.yaml` file and configure the services.
4.  In the Render dashboard, add your `GROQ_API_KEY` as a secret environment variable for the `rag-ai-agent-backend` service.
5.  Render will build and deploy your backend. Once it's live, you will get a URL for your backend service (e.g., `https://your-backend-url.onrender.com`).

### 2. Deploying the Frontend to Vercel

1.  **Update the `vercel.json` file**:
    In `agent-frontend/vercel.json`, replace `https://your-backend-url.onrender.com` with the actual URL of your deployed backend from Render.

2.  **Push the updated `vercel.json` to your GitHub repository.**

3.  **Deploy to Vercel**:
    *   Go to the [Vercel dashboard](https://vercel.com/new).
    *   Import your GitHub repository.
    *   Vercel will automatically detect that it's a Vite project.
    *   Set the **Root Directory** to `agent-frontend`.
    *   Deploy the project.

Vercel will build and deploy your frontend, and the rewrite rule in `vercel.json` will proxy API requests to your backend on Render.

## Project Structure

```
RAG-AI-Agent/
├── .gitignore
├── agent.py             # Core AI agent logic, Groq integration
├── app.py               # FastAPI backend application, API endpoints
├── database.py          # Database models and utilities
├── LICENSE              # MIT License
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── vector_database.py   # Vector database operations (ChromaDB)
├── .env                 # Backend environment variables (e.g., GROQ_API_KEY)
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
└── images/              # Project images
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, collaborations, or new projects, feel free to reach out to Kiran S. Hegde at [kiran.s.hegde.05@gmail.com](mailto:kiran.s.hegde.05@gmail.com).
