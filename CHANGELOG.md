# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-05-14

### Added
- **Phase 4 — Part 1**: OpenRouter LLM Provider.
  - `OpenRouterProvider` class implementing `LLMProvider` ABC with async HTTP, JSON mode enforcement, exponential backoff retry (3 attempts), Pydantic response parsing, and token usage tracking.
  - Provider factory `get_provider()` — reads `ENVFORGE_LLM_PROVIDER` env var and instantiates the correct provider with lazy imports.
  - New config fields: `ai_max_tokens` (default 2048), `ai_temperature` (default 0.3).
  - ADR-009: OpenRouter as Primary LLM Gateway.
- **Phase 4 — Part 2**: Prompt Engineering System.
  - System prompt constants with non-negotiable safety rules, JSON-only output enforcement, and available repair template IDs.
  - `TroubleshootPromptBuilder` class — converts DiagnosticReport + profile context into structured LLM user messages with CUDA matrix injection and prompt injection sanitisation.
  - `TroubleshootRequest` Pydantic model — structured input contract for the AI troubleshoot endpoint.
  - `LLMResponseMeta` model for audit logging (provider, model, token usage).
- **Phase 4 — Part 3**: Troubleshoot Service + API Endpoint.
  - `AITroubleshootService` orchestrator — full pipeline: prompt build → LLM call → safety filter → DB persist → audit log.
  - `POST /api/v1/troubleshoot` endpoint with structured error handling (503 for LLM errors, 500 for safety violations).
  - Registered troubleshoot router in FastAPI app.
- **Phase 4 — Part 4**: Repair Script Generation.
  - `RepairService` — maps AI-suggested template IDs to Jinja2 repair scripts, renders with validated params, safety-filters output.
  - 5 repair Jinja2 templates: `repair_cuda_upgrade`, `repair_python_install`, `repair_driver_update`, `repair_venv_recreate`, `repair_pip_reinstall`.
  - `POST /api/v1/repair` endpoint — generates repair scripts from template ID + params.
  - `GET /api/v1/repair/templates` endpoint — lists available repair templates.
  - All repair scripts include user confirmation prompts before making changes.
- **Phase 4 — Part 5**: Frontend API Types.
  - `backend/app/schemas/ai.py` — API-layer Pydantic schemas for troubleshoot and repair endpoints.
  - `frontend/src/types/index.ts` — Added `TroubleshootRequest`, `TroubleshootResponse`, `SuggestedFix`, `RepairRequest`, `RepairResponse`, `RepairTemplateInfo` TypeScript interfaces.
  - `frontend/src/services/api.ts` — Added `troubleshoot()`, `generateRepair()`, `getRepairTemplates()` API methods with structured error handling.
- **Phase 4 — Part 6**: Frontend Chat UI.
  - `frontend/src/app/troubleshoot/page.tsx` — Full AI Troubleshoot page with:
    - Diagnostic JSON input with sample data prefill
    - Profile selector and issue description field
    - Expandable fix cards with severity badges (CRITICAL/WARNING/INFO)
    - Diagnostic command display with one-click copy
    - Repair script generation, preview, copy, and download (.sh)
    - Animated confidence bar and premium glassmorphism design
  - Added "AI Troubleshoot" nav link to global layout.
- **Phase 4 — Part 7**: Rate Limiting.
  - In-memory sliding-window rate limiter with abstract `RateLimitBackend` (swappable for Redis).
  - Pre-configured limits: AI troubleshoot (10/min), repair (20/min), general (60/min).
  - Applied to `POST /api/v1/troubleshoot` and `POST /api/v1/repair` as FastAPI dependencies.
  - Standard HTTP 429 responses with `Retry-After` header.
  - X-Forwarded-For support for proxy deployments.
  - New config fields: `rate_limit_ai_rpm`, `rate_limit_repair_rpm`, `rate_limit_general_rpm`.

## [0.3.0] - 2026-05-14

### Added
- **Phase 3 Complete:** Next.js Frontend Web Application.
- Interactive Profile Browser displaying environment templates, capabilities, and pre-configured packages.
- Script Generation Wizard with dynamic dependency locking (Python/CUDA version auto-population based on profile restrictions).
- Diagnostic Dashboard with hardware overview cards, profile compatibility checker, structured issue rendering with severity badges, and one-click navigation to the Script Wizard.
- API client wrapper for seamless communication with the FastAPI backend.
- Vercel deployment configuration for edge-optimized hosting.
- Documentation updates for Phase 3 (Architecture, Workflows, Script Wizard Feature Doc, Diagnostic Dashboard Feature Doc).
- ADR-007: Dynamic UI Form Validation for Compatibility Engine.
- ADR-008: Safety Filter Negative Lookahead for Docker Cleanup Commands.

### Fixed
- Re-aligned frontend `PackageDef` interface with backend `PackageSpecSchema` to ensure accurate package rendering.
- Re-aligned frontend `ScriptGenerationResponse` interface — replaced stale `files_generated: string[]` with correct `scripts: ScriptPreview[]` structure to prevent `Cannot read properties of undefined` crash on results page.
- Re-aligned frontend `DiagnosticResponse` interface — replaced stale `{compatible, errors}` with correct `{report_id, compatible_profiles, issues, recommendations}` structure to match backend `DiagnoseResponse`.
- Resolved `422 Unprocessable Content` API error by adding strict `python_version` and `cuda_version` state tracking to the generation wizard.
- Fixed 500 Internal Server errors during profile fetching by enabling `from_attributes = True` on backend ORM schemas.
- Fixed Safety Filter false positive: regex `rm\s+-[rRf]{1,3}\s+/` was blocking legitimate Docker `rm -rf /var/lib/apt/lists/*` cleanup. Narrowed to `rm\s+-[rRf]{1,3}\s+/(?!\w)` using a negative lookahead.
- Fixed doubled download URL (`/api/v1/api/v1/...`) by stripping the `/api/v1` prefix from the base URL before appending the backend's `download_url`.
- Added null-safety guards for `profile.description` and `profile.tags` on the profiles listing page to prevent crashes when these optional fields are null.
- Removed trailing slashes in Vercel `NEXT_PUBLIC_API_URL` to fix `Failed to fetch` errors in production.

## [0.2.0] - 2026-05-06

### Added
- **Phase 2 Complete:** CLI Diagnostic Agent (`envforge-agent`).
- OS detection for Windows, Linux, and WSL2.
- GPU detection via `nvidia-smi`.
- CUDA toolkit, cuDNN, and NCCL version detection.
- Python installation scanner.
- RAM and CPU profiling.
- CLI commands: `envforge diagnose`, `envforge verify`, and `envforge fix`.
- Test suite with multi-platform fixtures.
- Documentation updates for CLI Agent deep-dive.

## [0.1.0] - 2026-05-06

### Added
- **Phase 1 Complete:** Core Backend implementation.
- FastAPI server with async PostgreSQL database (SQLAlchemy 2.0).
- Pure, deterministic Compatibility Engine for resolving package versions.
- Jinja2 Template Engine with a strict regex-based `SafetyFilter`.
- Generation of `setup.sh`, `setup.ps1`, `requirements.txt`, `Dockerfile`, and `devcontainer.json`.
- REST API endpoints for profiles, diagnostics, and script generation.
- Idempotent YAML seed service with 6 starter profiles (e.g., `pytorch-cuda`, `yolov8`).
- AI Layer skeleton with mock provider and Pydantic schemas.
- Comprehensive documentation suite (Architecture, ADRs, Workflows).
