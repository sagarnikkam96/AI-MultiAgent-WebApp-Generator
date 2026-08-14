# RAG Integration Point — PLANNED / FUTURE FUNCTIONALITY

> **STATUS: PLANNED — NOT IMPLEMENTED**
>
> The AI Multi-Agent Web Application Generator does **not** currently have an RAG pipeline,
> vector database, or embedding model. This document describes the **proposed** future
> integration point so the "Curated Software Development Knowledge Base" can be connected
> to retrieval-augmented generation without disturbing the existing working workflow.

## Current state (as of this writing)

- **Existing RAG:** NO
- **Existing vector database:** NO
- **Existing embeddings:** NO
- **Knowledge base connected to RAG:** NO

The current pipeline is deterministic + LLM-assisted and does **not** perform vector
retrieval. See the existing agents in `backend/app/agents/`.

## Proposed future architecture

The knowledge base in this folder would become the **retrieval corpus** for a future RAG
step that runs between requirement analysis and planning.

```
User Requirement
        ↓
Requirement Analysis            (existing: RequirementAgent)
        ↓
Knowledge Retrieval / Technical Context   ← PLANNED RAG STEP (new)
        ↓
Planning Agent                  (existing: PlannerAgent)
        ↓
Backend Agent                   (existing)
        ↓
Database Agent                  (existing)
        ↓
Frontend/Code Generation        (existing)
        ↓
Generated Web Application
```

## Proposed integration points (for a future implementation)

1. **Corpus source**
   The Markdown files under `knowledge_base/**/*.md` are the source documents.

2. **Chunking strategy**
   Each `.md` file can be split on headings (`##` / `###`) into logical chunks of a few
   paragraphs each. A `title` + `category` + `tags` field per chunk aids retrieval.

3. **Embedding model**
   Use the local Ollama server (already integrated as `OllamaClient`) with an embedding
   model if available; otherwise a small local sentence/token embedding model. This keeps
   the architecture local and consistent with the existing Ollama integration.

4. **Vector store**
   A lightweight local vector store (or PostgreSQL `pgvector` since PostgreSQL is already
   in the stack) would hold the chunk embeddings with metadata (path, category, topic).

5. **Retrieval trigger**
   During the pipeline, after `RequirementAgent.analyze()` produces structured requirements,
   a retrieval step would embed the requirement keywords/modules and return the top-K
   relevant knowledge chunks. These chunks would be injected into the planner, backend, and
   database prompts as "technical context".

6. **No changes to existing code required for this step**
   The knowledge base and this document are inert (documentation only). No application code
   was modified to add them. Wiring retrieval in later is an isolated, additive change.

## Guidelines for the future implementation

- Keep retrieval **additive**: add a new step rather than rewriting existing agents.
- Keep the existing Ollama integration and models unchanged.
- Never allow retrieved context to override explicit user requirements.
- Keep performance bounded (small corpus → low latency; cache embeddings on disk).
