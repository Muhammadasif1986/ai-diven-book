# 🚀 Application Run Guide (sp.run.md)

This document explains how to start the complete RAG system locally:

- 🧠 FastAPI RAG Backend  
- 📘 Docusaurus Book Website  
- 🤖 Embedded Chatbot Widget (Full-book + Selected-text mode)  
- 🔗 End-to-end Integration

---

# 🧠 1. Start the Backend (FastAPI RAG Server)

### Directory
```
/backend
```

### Run
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Backend URL
```
http://localhost:8000
```

### Expected Response
```json
{"message": "RAG Chatbot API is running!"}
```

### Important Endpoints
| Purpose | Endpoint |
|--------|----------|
| Health Check | `/health` |
| Full Book Query | `/rag/query` |
| Selected Text Query | `/rag/query/selection` |

Backend must load embeddings from Qdrant and metadata from Neon Postgres.

---

# 📘 2. Start the Docusaurus Book Website (Frontend + Chatbot UI)

### Directory
```
/my-website
```

### Run
```bash
cd my-website
npm install    # first time only
npm run start
```

### Docusaurus URL
```
http://localhost:3000
```

*(If port 3000 is busy → auto-shifts to 3001.)*

---

# 🤖 3. Chatbot Integration (Frontend Auto-Embed Verification)

Your chatbot widget must appear on the bottom-right of the Docusaurus site.

### Required Files

#### ✔ Chatbot Component
```
/my-website/src/components/Chatbot/index.tsx
```

#### ✔ Chatbot Styles
```
/my-website/src/components/Chatbot/chatbot.css
```

#### ✔ Chatbot Plugin
```
/my-website/plugins/rag-chatbot/index.js
/my-website/plugins/rag-chatbot/injectChatbot.js
```

#### ✔ Plugin Registration
In:
```
/my-website/docusaurus.config.ts
```

You must have:

```ts
plugins: ["./plugins/rag-chatbot"],
```

#### ✔ Environment Variable
Create:
```
/my-website/.env
```

Add:

```
RAG_API_URL=http://localhost:8000
```

---

# 🔗 4. How the System Works Together

```
User → Chatbot Widget → FastAPI Backend
        ↓                      ↓
    Full Book RAG        Qdrant + Postgres
        ↓                      ↓
  AI Answer → Chatbot UI → User
```

### Supported Modes
| Mode | Description |
|------|-------------|
| **Full-book Q&A** | Answer questions from entire book content |
| **Selected-text Q&A** | User highlights text → chatbot answers using ONLY selected content |

---

# 🧪 5. Verification Checklist

### ✔ Backend
Visit:
```
http://localhost:8000/health
```

Expected:
```
{ "status": "ok" }
```

### ✔ Chatbot Widget Visible
Open:
```
http://localhost:3000
```

You must see:

- A floating chatbot button  
- Chat window opens on click  
- Messages send correctly  
- Responses appear  

### ✔ Selected Text Mode
1. Highlight text in book  
2. Right-bottom chatbot → click **“Ask Selected Text”**  
3. Backend uses only the selected text for context  

---

# 🟢 6. Quick Start Using 2 Terminals

### Terminal 1 — Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 — Docusaurus Website
```bash
cd my-website
npm run start
```

---

# 🧩 7. Troubleshooting (If Chatbot Does NOT Appear)

| Issue | Reason | Fix |
|------|--------|------|
| Chatbot widget missing | Plugin not injected | Ensure `plugins: ["./plugins/rag-chatbot"]` |
| API errors | Wrong env variable | Check `.env` → `RAG_API_URL` |
| CORS error | Backend missing CORS | Add CORS middleware in FastAPI |
| No response | Wrong endpoint | Check `/rag/query` & `/rag/query/selection` |
| Button visible, widget empty | Missing CSS | Check `chatbot.css` import |
| JS errors | Wrong paths after structure changes | Run `/sp.analyze` |

---

# 🛠 8. Using SpecifyPlus + Claude Code

### Analyze full system
```
/sp.analyze
```

### Generate missing tasks
```
/sp.plan
```

### Execute tasks
```
/sp.execute
```

### Re-run after code changes
```
/sp.run
```

---

# 🎉 Done!

Your entire Docusaurus + FastAPI + RAG Chatbot system is now ready to run locally with full integration and debugging support.

