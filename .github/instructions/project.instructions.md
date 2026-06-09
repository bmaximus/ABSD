---
applyTo: "working/src/**"
---

# [Project Name] — Project Conventions

These instructions apply to all code produced for this project.
Fill in each section before the first cycle begins, then keep it updated as the project evolves.

---

## Solution / Project Structure

```
[Describe the top-level layout here — solution file, source folders, test folders, etc.]
```

---

## Layer Rules

### [Layer 1 — e.g. Domain / Core]
- Contains: [entities, enums, value objects, etc.]
- Dependencies: [none / only internal]

### [Layer 2 — e.g. Application / Business Logic]
- Contains: [handlers, services, interfaces, DTOs, validators]
- References: [Layer 1 only]

### [Layer 3 — e.g. Infrastructure / Data]
- Contains: [DB context, repositories, external service implementations]
- References: [Layer 1 and Layer 2]

### [Layer 4 — e.g. API / Presentation]
- Contains: [controllers, middleware, routing, startup]
- References: [Layer 2 only]

---

## Naming Conventions

### Backend
- [Document casing rules for classes, methods, fields, interfaces, etc.]
- [Document naming patterns for commands, queries, handlers, validators, DTOs]

### Frontend (if applicable)
- [Document casing rules for files, components, hooks, types, services]

### Database
- [Document casing for tables, columns, constraints, indexes]

---

## Build & Test

- **Build Command:** `[e.g. dotnet build / npm run build / cargo build ./...]`
- **Test Command:** `[e.g. dotnet test / npm test / pytest]`
- **Dev Server:** `[e.g. dotnet run / npm run dev]`

---

## API Response Format

```
[Describe the standard envelope for success and error responses]
```

---

## Validation Rules

- [List key input validation rules that apply across the project]

---

## Security Rules (Non-Negotiable)

- [List the project's non-negotiable security requirements]
- No raw query string building — use parameterized queries / ORM only
- No secrets in source code — use environment variables / secret manager
- Production error responses must NOT include stack traces

---

## Testing Conventions

- [Framework and mocking approach]
- [Test file naming conventions]
- [Unit vs integration test rules]
- Test naming: `[pattern, e.g. MethodName_Scenario_ExpectedResult]`
