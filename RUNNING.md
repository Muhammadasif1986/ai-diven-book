# Running the AI-Diven Book System

This document explains how to run the complete integrated system with Docusaurus frontend, FastAPI backend, and RAG chatbot.

## Prerequisites

- Node.js v20+
- Python 3.11+
- Access to Qdrant vector database (configured via environment variables)
- Access to OpenAI API (configured via environment variables)

## Running the Complete System

### 1. Start the Backend Server

```bash
cd backend
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 2. Start the Docusaurus Frontend

In a separate terminal:

```bash
cd my-website
npm run start
```

The Docusaurus site will be available at `http://localhost:3001` (or the next available port) with the API proxy configured to forward `/api` requests to the backend.

### 3. Using the Integrated Chatbot

- The chatbot will appear as a floating button on all pages of the Docusaurus site
- Click the button to open the chat interface
- Ask questions about the book content
- The chatbot will use the RAG system to provide context-aware responses

## Development Configuration

The development setup includes:

- **API Proxy**: Docusaurus development server proxies `/api` requests to the backend at `http://localhost:8000`
- **Hot Reloading**: Both frontend and backend support hot reloading during development
- **Session Management**: Chat sessions are persisted using localStorage

## Environment Variables

Make sure your environment variables are properly set in both directories:

**Backend** (`backend/.env`):
```
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
QDRANT_URL=your_qdrant_url
DATABASE_URL=your_database_url
```

## Production Build

To build the static site for production:

```bash
cd my-website
npm run build
```

Note: The PDF generation plugin is available but commented out by default due to build complexity. To enable it, uncomment the plugin configuration in `docusaurus.config.ts`.

## Troubleshooting

1. **API requests failing**: Ensure the backend server is running on port 8000
2. **Chatbot not appearing**: Check browser console for errors and ensure the Root.tsx component is properly configured
3. **Build issues**: If the PDF plugin causes build issues, keep it commented out in production