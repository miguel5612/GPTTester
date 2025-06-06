# GPTTester Backend

This folder contains a minimal FastAPI backend prepared for future integration with the GPTTester project. It provides JWT-protected CRUD endpoints for managing users, tests, clients, projects and test plans. User registration validates usernames and password strength and stores passwords securely. Login is protected with simple rate limiting to mitigate brute force attacks. Test plans are modeled following ISTQB and Business Centric Testing guidance.
The system defines four roles: **Administrador**, **Arquitecto de Automatización**, **Automation Engineer** and **Analista de Pruebas con skill de automatización**. On first run an `admin` user with password `admin` is created and granted the *Administrador* role. Only administrators may manage roles, clients, projects or assign them to other users. Projects are only visible to their assigned analysts or administrators.

## Setup

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Set the `DATABASE_URL` environment variable for your Postgres instance:

```
export DATABASE_URL=postgresql://user:password@localhost/db
```

Run the application with:

```bash
uvicorn app.main:app --reload
```

## TestPlan API

Test plans follow ISTQB and Business Centric Testing guidance. Each test plan
requires a unique **nombre** of at least five characters and can describe the
objective, scope, entry/exit criteria, test strategy, responsible persons, start
and end dates and BDD story links.

Available endpoints under `/testplans` allow administrators to create, update and
delete plans while any authenticated user can list or view them.

## Screenplay Pages API

Pages represent screens of the application and contain reusable elements for the
Screenplay pattern. Administrators manage pages and elements. Elements are unique
per page and can be linked to scenarios for reuse.

Main routes:

- `/pages` CRUD for pages
- `/pages/{page_id}/elements` CRUD for elements on a page
- `/elements/{element_id}/scenarios/{scenario_id}` attach or detach an element
  to a scenario
- `/scenarios` CRUD for test scenarios

## Automation Actions API

Actions define reusable automation steps like clicking or typing. Each action
includes a name, type, executable code snippet and required arguments. Unsafe
code patterns are rejected. Administrators manage actions while any
authenticated user can view them.

Main routes:
- `/actions` CRUD for automation actions

## Action Assignments API

Action assignments link an existing automation action with a specific page element and test case, providing concrete argument values. All parameters required by the action must be supplied.

Main routes:
- `/assignments` CRUD for action assignments

## Execution Agents API

Agents represent the machines or devices that run automated tests. Each agent
has an **alias**, unique **hostname** and a supported operating system
(Windows, Linux, Mac, Android or iOS). Android and iOS agents may be tagged with
the special category `granja móvil`.

Main routes:
- `/agents` CRUD for execution agents

## Execution Plans API

Execution plans specify which TestCase should run on which execution agent. A plan includes a required `nombre`, the `test_id` of an existing TestCase and the `agent_id` of the responsible agent. Plans can be listed and filtered by plan name, test or agent to provide execution history.

Main routes:
- `/execution-plans` CRUD for execution plans with optional query parameters `nombre`, `test_id` and `agent_id` for filtering
- `/execution-plans/{plan_id}/execute` trigger a plan execution and create an execution record

## Executions API

Agents can check if they have a pending execution assigned using:

- `/executions/pending?hostname=<hostname>` – returns the full hierarchy of the pending plan, including the TestCase and its assigned actions and page elements. Agents must authenticate and only access executions matching their hostname.
- `/executions/{id}/report` (POST) – upload a PDF or ZIP report for the given execution. Only the assigned agent may upload the file.
- `/executions/{id}/report` (GET) – download the previously uploaded report. Administrators or the agent can access it.

## Postman Collection

After installing the backend dependencies you can generate a Postman
collection that covers every API endpoint:

```bash
python postman/generate_collection.py
```

The script writes `postman/GPTTester.postman_collection.json` and
`postman/GPTTester.environment.json`. Import both files in Postman to start
testing. The environment defines the `base_url` of the API and a `token`
variable for authenticated requests.
