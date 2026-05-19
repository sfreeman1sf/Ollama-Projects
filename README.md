# Ollama-Projects

### Local LLM Experiments & AI Assistant Development

A collection of Python projects exploring local AI models via Ollama, combining personal assistant capabilities with NLP pattern recognition on real-world testimony data.

---

## Projects

### 1. Stacey Assistant — Voice-Activated Local AI
A personal AI assistant running on local LLMs (Gemma 3, LLaMA 3.2) via Ollama.

**Features:**
- Voice activation and text input
- Google Calendar API integration
- Persistent memory across sessions
- Event creation, editing, and retrieval

**To Run:**
```bash
ollama serve
cd Desktop/stacey_calendar
python stacey_assistant.py
```

---

### 2. Testimony Pattern Recognition System
A data pipeline using hash tables and priority queues to analyze anonymous testimonies from individuals who turned their lives around.

**Components:**
- `hash_table.py` — Stores and retrieves anonymous testimony data
- `priority_queue.py` — Ranks and surfaces behavioral patterns
- `test_program.py` — RAG pipeline development and testing

**Next Phase:** RAG integration to train a local model on the testimony dataset.

---

## Stack

`Python` `Ollama` `Gemma 3` `LLaMA 3.2` `Google Calendar API` `SQLite`

---

## Author

**Stacey Freeman**
Master's Candidate — Artificial Intelligence & Machine Learning

---

## Status

| Component | Status |
|---|---|
| Voice Assistant | ✅ Complete |
| Google Calendar Integration | ✅ Complete |
| Hash Table / Testimony Data | ✅ Complete |
| Priority Queue Pattern Recognition | ✅ Complete |
| RAG Pipeline | 🔄 In Progress |