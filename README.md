# EnvForge

> **Intelligent ML/AI Environment Provisioning Platform**

EnvForge generates production-ready setup scripts, diagnoses ML environments,
and provides AI-assisted troubleshooting for Windows, WSL, Linux, and CUDA systems.

---

## What it Does

| Capability | Description |
|-----------|-------------|
| 🧩 **Profile Browser** | Browse pre-validated ML environment profiles (PyTorch, TensorFlow, YOLOv8, etc.) |
| ⚙️ **Script Generation** | Download `setup.sh`, `setup.ps1`, `requirements.txt`, `Dockerfile`, `devcontainer.json` |
| 🔍 **Local Diagnostics** | CLI agent inspects your GPU, CUDA, drivers, Python — outputs structured report |
| ✅ **Verification** | Verify your environment meets framework requirements |
| 🤖 **AI Troubleshooting** | AI explains issues and suggests safe, ordered fix steps |
| 🔧 **Repair Scripts** | Generate targeted repair scripts for broken environments |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14+, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.11+, Pydantic v2 |
| Database | PostgreSQL, SQLAlchemy 2.0 async, Alembic |
| Templates | Jinja2 |
| CLI Agent | Python (standalone pip package) |
| AI Layer | Pluggable LLM (OpenAI / OpenRouter / Ollama) |

---

## Quick Start (Development)

> ⚠️ Full setup guide coming in Phase 0 completion.

```bash
git clone https://github.com/your-org/envforge
cd EnvForge
docker-compose up -d
```

---

## Documentation

All documentation lives in [`docs/`](./docs/):

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System architecture and layer design |
| [FEATURES.md](./docs/FEATURES.md) | Feature specifications |
| [ROADMAP.md](./docs/ROADMAP.md) | Development phases and milestones |
| [API_DESIGN.md](./docs/API_DESIGN.md) | REST API endpoint specifications |
| [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) | PostgreSQL schema design |
| [COMPATIBILITY_ENGINE.md](./docs/COMPATIBILITY_ENGINE.md) | Version resolution logic |
| [TEMPLATE_SYSTEM.md](./docs/TEMPLATE_SYSTEM.md) | Jinja2 script generation |
| [AI_LAYER.md](./docs/AI_LAYER.md) | AI reasoning and safety design |
| [WORKFLOW.md](./docs/WORKFLOW.md) | End-to-end user workflows |
| [PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md) | Folder structure guide |
| [decisions/](./docs/decisions/) | Architecture Decision Records |

---

## Engineering Principles

- **Deterministic**: Same inputs always produce the same scripts
- **Safe**: No destructive shell commands; AI output always sanitized
- **Modular**: Clean separation between API, services, engine, templates, AI
- **Typed**: Pydantic v2 models throughout; TypeScript on frontend
- **Tested**: Compatibility engine targets 100% unit test coverage
- **Contributor-friendly**: Clear ADRs, docs, and structural rules

---

## Status

🚧 **Phase 0 — Foundation / Architecture Design**

See [ROADMAP.md](./docs/ROADMAP.md) for the full development plan.

---

## License

MIT
