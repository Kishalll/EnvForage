# Script Generation Wizard (Phase 3)

> **Status**: ✅ Implemented
> **Last Updated**: 2026-05-14

## Overview

The Script Generation Wizard is the core feature of the EnvForge Web Application (Frontend). It provides an intuitive, step-by-step user interface that allows developers to select an environment profile and configure it to generate deterministic setup scripts.

## Architecture & Data Flow

The wizard operates entirely on the client side (Next.js) and communicates with the FastAPI backend to fetch profiles and generate scripts.

1. **Step 1: Profile Selection**
   - Fetches available profiles from `GET /api/v1/profiles`.
   - Displays profiles with their names, descriptions, and tags.
   - User selects a base profile (e.g., `pytorch-cuda`, `yolov8`).

2. **Step 2: Configuration**
   - Based on the selected profile's capabilities (e.g., `os_support`, `python_versions`, `cuda_required`), the wizard dynamically populates configuration dropdowns.
   - **Target OS**: LINUX, WSL, or WIN. Options are disabled if the profile does not support them.
   - **Output Formats**: Selectable formats like `setup.sh`, `setup.ps1`, `requirements.txt`, and `Dockerfile`.
   - **Python Version**: Dynamically loaded from the profile's `python_versions` list.
   - **CUDA Version**: Shown only if `cuda_required` is true or if the profile supports optional CUDA. Loaded from `cuda_versions`.

3. **Step 3: Generation & Download**
   - The frontend constructs a `ScriptGenerationRequest` payload and sends it to `POST /api/v1/scripts/generate`.
   - The backend Compatibility Engine validates the request, applies constraints, and templates the scripts.
   - The frontend receives a `GenerationResponse` containing a job ID and a download URL.
   - User downloads the generated artifact bundle (ZIP) containing all requested scripts.

## Frontend Payload

The `ScriptGenerationRequest` constructed by the wizard ensures all required fields are passed to the backend, preventing `422 Unprocessable Content` errors:

```json
{
  "profile_id": "pytorch-cuda",
  "target_os": "LINUX",
  "output_formats": ["setup.sh", "requirements.txt"],
  "python_version": "3.11",
  "cuda_version": "12.1"
}
```

## Relevant Files

- `frontend/src/app/generate/page.tsx`: The main multi-step wizard component.
- `frontend/src/types/index.ts`: TypeScript definitions matching backend Pydantic models.
- `frontend/src/services/api.ts`: API wrapper for communicating with the backend.
