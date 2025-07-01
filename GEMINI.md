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

## Railway Deployment

This section outlines the steps for deploying the `brand-audit-app` to Railway.

### 1. Railway CLI Installation

Ensure you have the Railway CLI installed and authenticated:

```bash
curl -fsSL https://railway.app/install.sh | bash
railway login
```

### 2. Project Setup on Railway

Navigate to the root of your `brand-audit-app` project and initialize Railway:

```bash
railway init
```

Follow the prompts to link to an existing project or create a new one.

### 3. Environment Variables

Ensure all necessary environment variables (e.g., `OPENROUTER_API_KEY`, `NEWS_API_KEY`, `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`) are configured on Railway. You can set them via the Railway dashboard or CLI:

```bash
railway env add VARIABLE_NAME=your_value
```

### 4. Deployment

Deploy the application. Railway will automatically detect the `backend` (Python/Flask) and `frontend` (Node.js/Vite) services and deploy them.

```bash
railway up
```

### 5. Post-Deployment Verification

After successful deployment, verify the application's functionality:

- **Access Frontend**: Open the Railway-provided URL for your frontend service in a browser.
- **Test Backend API**: Use `curl` or a tool like Postman to test backend API endpoints (e.g., `curl https://your-railway-backend-url.railway.app/api/health`).
- **End-to-End Workflow**: Manually test the full user workflow (registration, login, analysis, report generation) on the deployed application.

---

## Verification Commands

The following commands must be run from their respective directories (`backend` or `frontend`) before creating a pull request, and then adapted for post-deployment verification.

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
    pnpm lint
    ```
