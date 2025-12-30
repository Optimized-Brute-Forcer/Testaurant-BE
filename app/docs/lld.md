# Low Level Design - Testaurant

## 1. System Overview

Testaurant is an advanced automated testing platform designed to simplify the validation of backend services, including REST APIs, SQL Databases (MySQL/PostgreSQL), and NoSQL Databases (MongoDB). It provides a unified interface for defining, executing, and monitoring test cases, with features like role-based access control (RBAC), environment management, and execution auditing.

## 2. Technical Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React, TypeScript, Monaco Editor, CSS3 |
| **Backend** | FastAPI (Python), Motor (Async MongoDB), Pydantic |
| **Database** | MongoDB |
| **Infrastructure** | Netlify (Frontend/BFF Proxy), AWS EC2 (Backend Services) |
| **Authentication** | Google OAuth 2.0, JWT (JSON Web Tokens) |

## 3. Database Architecture

The system uses MongoDB as its primary persistence layer. All interactions are handled asynchronously via the `motor` driver.

### 3.1 Schema Definition

| Collection | Role | Key Fields |
| :--- | :--- | :--- |
| `organizations` | Multi-tenant root | `organization_id`, `name`, `teams`, `members` |
| `users` | User profiles | `email`, `google_id`, `role`, `organization_id` |
| `workitem_master` | Atomic test units | `workitem_id`, `type`, `config`, `expected_response` |
| `testcase_master` | Sequences of workitems | `testcase_id`, `workitem_list`, `organization_id` |
| `testsuite_master` | Logical groupings | `testsuite_id`, `testcase_list`, `organization_id` |
| `env_config` | Environment variables | `config_key`, `environment`, `value`, `organization_id` |
| `run_workitem_audit` | Execution history | `run_id`, `workitem_id`, `status`, `latency_ms` |
| `counter_master` | Atomic ID generation | `counter_name`, `sequence_value` |

## 4. System Architecture

```mermaid
graph TD
    User["User (Browser)"] -->|HTTPS| Frontend["Testaurant UI (React)"]
    Frontend -->|API Requests (JWT)| BFF["FastAPI Backend (EC2)"]
    
    subgraph "Backend Services"
        BFF -->|Async CRUD| Mongo[("MongoDB Atlas")]
        BFF -->|REST Client| ExtAPI["External REST APIs"]
        BFF -->|SQL Client| ExtSQL[("External SQL DBs")]
        BFF -->|NoSQL Client| ExtMongo[("External MongoDB")]
    end

    subgraph "Core Modules"
        Auth["Auth Module (Google OAuth)"]
        Org["Org & RBAC Module"]
        Exec["Execution Engine"]
        Audit["Audit & Logging"]
    end

    BFF --> Auth
    BFF --> Org
    BFF --> Exec
    Exec --> Audit
```

## 5. Core Component Logic

### 5.1 Authentication & RBAC

The system implements a secure authentication flow using Google Identity.

- **Login**: Frontend exchanges a Google ID Token for a system-issued JWT.
- **Roles**: 
    - `ADMIN`: Full access to organization, member management, and configurations.
    - `MEMBER`: Can create and execute tests.
    - `VIEWER`: Read-only access to tests and reports.
- **Tenancy**: Every request is scoped by `organization_id` extracted from the JWT.

### 5.2 Execution Engine (Deep Dive)

The `ExecutionService` is responsible for running tests across different protocols.

#### 5.2.1 REST Execution
- Uses `httpx.AsyncClient` for non-blocking I/O.
- Supports dynamic header injection and body parsing.
- Validates status codes and response structures.

#### 5.2.2 SQL Execution
- Utilizes `aiomysql` and `sqlalchemy` for asynchronous database connections.
- Executes safe, parameterized queries.
- Parses result sets for assertion checking.

#### 5.2.3 Feed-Forward Mechanism (Planned)
- Allows capturing data from one workitem's response and injecting it into the next workitem's request in a testcase.

### 5.3 Audit Trails

Every execution generates an audit record in the respective collection (`run_workitem_audit`, `run_testcase_audit`, etc.). This ensures:
- Full traceability of test results.
- Performance monitoring over time.
- Debugging capabilities with full request/response payloads stored.

## 6. API Interface

The backend exposes a RESTful API organized into controllers:

- **Auth Controller**: `/auth/login`, `/auth/verify`
- **Organization Controller**: `/organization/create`, `/organization/join`, `/organization/members`
- **BFF Controller**: 
    - `/bff/workitems`: CRUD for test units.
    - `/bff/testcases`: CRUD for sequences.
    - `/bff/testsuites`: CRUD for suites.
    - `/bff/run`: Triggers for execution.

## 7. Security Considerations

- **CORS**: Strict origin validation to prevent unauthorized cross-origin requests.
- **JWT**: Tokens are signed with a server-side secret and have short expiration times.
- **Credential Storage**: External DB credentials for testing are stored associated with organizations, with future plans for vault encryption.
