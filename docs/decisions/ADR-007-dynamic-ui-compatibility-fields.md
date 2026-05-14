# ADR-007: Dynamic UI Form Validation for Compatibility Engine

## Status
Accepted

## Context
During the implementation of Phase 3 (Next.js Frontend), we needed to design the UI for the Script Generation Wizard. 
The backend Compatibility Engine (Phase 1) is strictly deterministic and relies on specific constraints defined in the environment profiles (e.g., supported `python_versions` and `cuda_versions`). 

Initially, the frontend wizard allowed users to select basic parameters like Target OS and Output Formats. However, the backend's Pydantic schema for `/api/v1/scripts/generate` explicitly requires the `python_version` and dynamically requires `cuda_version` based on the profile's `cuda_required` flag. Failing to provide these resulted in a `422 Unprocessable Content` error.

## Decision
Instead of allowing free-text input for dependencies or handling the `422` error as a general user-facing error, we decided to tightly couple the UI generation to the profile constraints fetched from the backend. 

Specifically:
1. The frontend wizard dynamically generates dropdowns for Python and CUDA versions.
2. The options within these dropdowns are strictly populated from the `activeProfile.python_versions` and `activeProfile.cuda_versions` arrays.
3. The UI uses React hooks (`useEffect`) to automatically select the first valid option in the array as the default, ensuring the payload is never incomplete.

## Consequences

**Positive:**
- **Zero Invalid States:** The user is physically prevented from requesting a Python or CUDA version that the profile does not support, vastly reducing frustrating 409 or 422 errors.
- **Improved UX:** Sane defaults mean the user can simply click "Generate" without manually typing in dependency versions.
- **Strong Coupling:** The frontend perfectly respects the "Source of Truth" of the backend's seeded profile data.

**Negative:**
- The frontend `page.tsx` logic is slightly more complex, requiring dynamic mounting of form fields based on the selected profile's state.

## Related ADRs
- [ADR-001: REST over GraphQL](./ADR-001-rest-over-graphql.md) (established the JSON payload structures that this UI decision supports).
