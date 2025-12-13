# Quickstart Guide: Integrated RAG Chatbot for Docusaurus Book

## Overview
This guide provides quick instructions to get the RAG chatbot system up and running with your Docusaurus book.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for Docusaurus)
- Docker (optional, for local development)
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Postgres account (free tier)

## Setup Instructions

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your API keys and service URLs:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   QDRANT_COLLECTION_NAME=book_content_chunks
   NEON_DATABASE_URL=postgresql://username:password@ep-xxxx.us-east-1.aws.neon.tech/dbname
   ```

6. Start the backend server:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

### 2. Frontend Integration
1. Navigate to your Docusaurus directory:
   ```bash
   cd my-website  # or wherever your Docusaurus site is located
   ```

2. Install the chat widget dependency:
   ```bash
   npm install @site/src/components/ChatWidget
   ```

3. Add the chat widget to your Docusaurus layout (in `src/pages/layout.js` or similar):
   ```jsx
   import ChatWidget from '@site/src/components/ChatWidget/ChatWidget';

   export default function Layout({children}) {
     return (
       <>
         <main>{children}</main>
         <ChatWidget apiUrl="http://localhost:8000/api/v1" bookId="your-book-id" />
       </>
     );
   }
   ```

4. Start your Docusaurus site:
   ```bash
   npm run start
   ```

### 3. Ingest Your Book Content
1. Prepare your book content as Markdown files
2. Send a POST request to the ingest endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest \
     -H "Content-Type: application/json" \
     -d '{
       "book_id": "my-book",
       "title": "My Book Title",
       "content": "Full book content in Markdown format...",
       "author": "Author Name"
     }'
   ```

### 4. Using the Chatbot
Once everything is running:

1. **General Queries**: Type questions in the chat widget to ask about the entire book
2. **Selection-Based Queries**: Select text in the book content and click "Ask about this selection" to constrain queries to only the selected text
3. **View Citations**: All responses include citations showing the source of information

## API Endpoints
- `POST /api/v1/query` - Query the entire book
- `POST /api/v1/query/selection` - Query only selected text
- `POST /api/v1/ingest` - Ingest book content
- `GET /api/v1/health` - Health check

## Configuration
- Rate limiting: 10 requests per minute per IP
- Selection text limit: 5000 characters maximum
- Session tokens: Auto-generated for anonymous users
- Response timeout: 30 seconds

## Troubleshooting
- If you get rate limit errors, wait before sending more requests
- If the chat widget doesn't appear, check that you've properly integrated it in your Docusaurus layout
- If queries return no results, verify that content was properly ingested
- Check the backend logs for detailed error information

## Next Steps
1. Customize the chat widget styling to match your book's theme
2. Add your specific book content to the system
3. Configure proper API keys for production deployment
4. Set up monitoring for API usage and performance