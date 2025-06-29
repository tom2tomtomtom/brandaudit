# Gemini Development Protocol

This document outlines the strict protocol for making improvements and fixes to the `brand-audit-app` codebase. The primary goal is to ensure code quality, stability, and prevent catastrophic failures. All contributions made by Gemini must adhere to these guidelines.

## Core Mandates

1.  **Adhere to Conventions**: Rigorously follow existing project conventions. Analyze surrounding code, file structure, and configuration before writing any new code.
2.  **Verify Libraries/Frameworks**: NEVER assume a library is available or appropriate. Verify its established use within the project by checking `requirements.txt` (backend) or `package.json` (frontend) and observing existing import patterns.
3.  **Mimic Style and Structure**: All new code must match the style (formatting, naming), structure, and architectural patterns of the existing codebase.
4.  **Idiomatic Changes**: Ensure all changes integrate naturally with the local context, including imports, class/function structures, and variable naming.
5.  **High-Value Comments Only**: Add comments sparingly. Focus on *why* something is complex, not *what* it does. Do not add comments unless necessary for clarity.

---

## Safety and Development Workflow

To minimize risk, all changes, no matter how small, must follow this workflow.

### 1. Branching

- **No Direct Commits**: All work must be done in a new, descriptively named branch. Never commit directly to `main` or `develop`.
- **Branch Naming**:
  - For new features: `feature/a-brief-description`
  - For bug fixes: `fix/a-brief-description`

### 2. Understand and Plan

- **Analyze First**: Before writing code, use `read_file`, `list_directory`, and `search_file_content` to thoroughly understand the relevant code sections.
- **Formulate a Plan**: Create a clear, step-by-step plan for the proposed changes.
- **Confirm the Plan**: Present the plan for user approval before implementation.

### 3. Implement

- Write clean, readable, and maintainable code that adheres to the **Core Mandates**.

### 4. Verification (The Safety Net)

This is the most critical phase. No code will be merged until it passes all verification steps.

**A. Local Testing:**

- **Unit & Integration Tests**:
  - For any new feature, corresponding unit or integration tests **must** be added.
  - For any bug fix, a test that specifically targets the bug **must** be added to prevent regressions.
- **Run All Tests**: All existing and new tests for the relevant part of the application (frontend or backend) must pass.

**B. Linting and Static Analysis:**

- **Code Quality Gates**: The code must pass all automated linting and type-checking rules to ensure it meets project standards.

**C. Pull Request (PR):**

- **Create a PR**: Once local verification is complete, open a Pull Request.
- **Clear Description**: The PR description must clearly explain:
  - **What** was changed.
  - **Why** the change was necessary.
  - **How** the changes have been verified.
- **User Approval**: The PR must be reviewed and explicitly approved by the user before proceeding.

### 5. Merging

- Once the Pull Request has passed all checks and has been approved, the branch can be merged into the main development line.

---

## Verification Commands

The following commands must be run from their respective directories (`backend` or `frontend`) before creating a pull request.

### Backend (`/brand-audit-app/backend`)

1.  **Activate Virtual Environment**:
    ```shell
    source venv/bin/activate
    ```
2.  **Run Tests**:
    ```shell
    pytest
    ```
3.  **Run Linter & Formatter**:
    ```shell
    ruff check . && ruff format .
    ```
4.  **Run Type Checker**:
    ```shell
    mypy .
    ```

### Frontend (`/brand-audit-app/frontend`)

1.  **Run Tests**:
    ```shell
    pnpm test
    ```
2.  **Run Linter**:
    ```shell
t
    pnpm lint
    ```
