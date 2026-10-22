# LogicTree Academy

**Coding · Maths · Physics**

LogicTree Academy is an evolving technology and learning project exploring how software, interactive development tools, and AI-assisted systems can support learning in coding, mathematics, and physics.

This repository contains the backend and supporting services behind that work. It brings together application development, learning-content systems, developer tooling, infrastructure experiments, and educational AI research in one evolving codebase.

The project demonstrates practical engineering through the development of interconnected systems, from backend APIs and authentication to container management, real-time communication, file-system operations, and AI-oriented educational experiments.

---

## 1. Project Overview

LogicTree Academy explores the intersection of education, software engineering, and artificial intelligence.

The codebase includes several areas of development:

- **Backend engineering:** Django applications, APIs, application services, and account workflows.
- **Authentication and authorization:** User registration, login, password recovery, and permission-related functionality.
- **Learning systems:** Courses, lessons, tasks, answers, assignments, and educational content workflows.
- **Developer tools:** File and directory operations, terminal functionality, and interactive development environments.
- **Container infrastructure:** Docker-related functionality and experiments involving isolated execution environments.
- **Real-time systems:** WebSocket communication and Django Channels components.
- **Artificial intelligence:** Intent classification, educational content processing, topic handling, and CUBE learning-assistant experiments.
- **Frontend development:** React and TypeScript interfaces supporting different parts of the wider project.
- **Supporting services:** Separate Node.js services and infrastructure components that extend the backend's capabilities.

These components represent an evolving engineering codebase. Not every component should be assumed to be fully integrated, complete, or production-ready.

## 2. The Vision

The broader objective of LogicTree Academy is to explore how technology can make learning more practical, interactive, and accessible.

Rather than treating coding, mathematics, and physics as isolated subjects, the project explores opportunities to connect theoretical knowledge with software tools, experimentation, and implementation.

The engineering work extends beyond conventional educational content into the systems that could support interactive learning environments, including development tools, execution services, and AI-assisted functionality.

### Project Objectives

- **Connect learning and technology:** Explore ways to combine educational content with interactive software.
- **Develop practical tools:** Build systems that support coding, experimentation, and development workflows.
- **Explore AI-assisted learning:** Experiment with educational content processing and intelligent assistance.
- **Build integrated systems:** Develop backend services, APIs, and supporting infrastructure.
- **Advance through implementation:** Test ideas through real software development and continuous refinement.

## 3. Backend and Application Systems

The project uses Django as the foundation for its main backend, with additional services supporting different areas of functionality.

### Django Backend

The Django application provides the main project structure, including URL configuration, application modules, service logic, and backend functionality.

The codebase is organised into separate applications to support different responsibilities across the wider system.

### Authentication and Account Management

The authentication components explore account-related functionality, including:

- User registration and login.
- Password recovery and reset workflows.
- Email-related authentication functionality.
- Account information and profile-related operations.
- Authentication and authorization support.

### Learning Content Systems

The project includes components related to the organisation and processing of educational content.

These cover areas such as:

- Courses and learning modules.
- Lessons and educational material.
- Tasks and assignments.
- Answers and related learning workflows.
- Supporting APIs for learning-related functionality.

The objective is to establish backend functionality that can support structured educational experiences.

## 4. Developer Tools and Infrastructure

An important part of the project involves exploring the infrastructure required to support interactive software development.

### File-System Operations

The file-system components provide functionality for working with files and directories.

Related operations include file creation, reading, saving, renaming, moving, copying, and deletion.

These components form part of the broader exploration of browser-accessible development tools and file-management workflows.

### Container Management

The project includes Docker-related functionality for managing container-based environments.

Containerisation provides a foundation for experimenting with isolated execution environments and services that may require their own dependencies or runtime configurations.

### Terminal and Real-Time Communication

Terminal-related components explore interactive development functionality supported by separate services and real-time communication.

The implementation includes work involving Node.js, WebSockets, Django Channels, and Daphne.

These components represent the infrastructure-oriented side of the project, extending beyond conventional CRUD-based backend functionality.

### Supporting Execution Services

Additional directories contain supporting execution and container-related components.

Together, these experiments explore how development tools and backend services might be connected within a broader interactive learning environment.

## 5. Artificial Intelligence and CUBE

The repository includes CUBE-related experiments focused on educational content and AI-assisted functionality.

This work explores areas such as:

- Educational content extraction and processing.
- Topic-oriented content organisation.
- Formula and definition lookup.
- Intent classification.
- Structured intent-related processing.
- Dataset preparation and management.
- Machine-learning and model experimentation.

The codebase includes Python-based processing and machine-learning components, including work involving PyTorch.

CUBE represents an experimental part of the wider LogicTree direction. Its components and capabilities may evolve independently as the underlying ideas are tested and refined.

## 6. Technology Stack

The repository contains implementations and experiments using the following technologies.

| Technology | Purpose |
|---|---|
| Python | Backend development, data processing, and AI experiments |
| Django | Main backend application framework |
| Django REST Framework | API development |
| Django Channels | Asynchronous and real-time backend functionality |
| Daphne | ASGI application serving |
| Docker | Containerisation and infrastructure experiments |
| Node.js | Supporting backend and development services |
| Express | Node.js service development |
| WebSockets | Real-time communication |
| React | Component-based user interfaces |
| TypeScript | Typed frontend development |
| PyTorch | Machine-learning and model experiments |

Individual components may have separate dependencies and configurations. The technologies listed reflect the different areas of work represented in the repository rather than a claim that every technology is used by every component.

## 7. System Architecture

The project follows a modular approach in which different applications and services are responsible for specific areas of functionality.

The main Django backend provides the central application structure, while supporting services handle specialised responsibilities such as terminal functionality, file operations, container management, and AI-related processing.

### High-Level Architecture

```text
                    LOGICTREE ACADEMY
                            |
                            v
                    Main Django Backend
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
    Authentication    Learning Systems   Application APIs
          |                 |                 |
          +-----------------+-----------------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        File-System     Container       AI and CUBE
         Services       Tooling          Experiments
             |              |              |
             +--------------+--------------+
                            |
                            v
                 Supporting Applications
                 and External Services
```

This diagram illustrates the project's broad areas of responsibility. It is a conceptual overview rather than a guarantee that every component is directly connected or operational in a single deployment.

## 8. Repository Structure

The repository is organised into Django applications, supporting services, frontend projects, and AI-related components.

| Directory | Purpose |
|---|---|
| `servers/` | Django project configuration and application entry points |
| `authentication/` | Authentication and account-related workflows |
| `authorization/` | Authorization and permission-related functionality |
| `notes/` | Learning content, lessons, tasks, answers, and assignments |
| `filesystem/` | File and directory operations |
| `docker_manager/` | Container-management functionality |
| `terminal/` | Terminal-related application components |
| `terminal_server/` | Supporting terminal service |
| `terminal-backend/` | Terminal-related backend and frontend components |
| `intent_clarifier/` | Intent classification and clarification functionality |
| `intent_executor/` | Intent-related execution functionality |
| `cube/` | Educational content processing and CUBE experiments |
| `frontend/` | Frontend application components |
| `frontend-test/` | Additional frontend experiments |
| `filesystem-service/` | Supporting Node.js file-system service |
| `python-executor/` | Python execution-related components |
| `filesystem_container/` | File-system and container-related functionality |

The directory structure reflects the project's development history and may change as applications and services are refined.

## 9. Engineering Approach

LogicTree Academy is developed through practical experimentation and iterative implementation.

The project explores not only application-level features but also the infrastructure, integrations, and supporting services required to connect them.

### Modular Development

Separate applications and services help organise functionality according to its responsibilities.

### Practical Engineering

The project involves implementing real systems and investigating the challenges of connecting backend services, interfaces, infrastructure, and data processing.

### Experimentation and Refinement

Some components are experimental by design. The aim is to explore technical approaches, evaluate their usefulness, and refine the architecture as development progresses.

### Learning Through Building

The codebase reflects an approach centred on understanding software engineering through implementation, from application logic to infrastructure and AI-oriented experimentation.

## 10. Security and Development Status

This repository represents an evolving development project and should not be interpreted as confirmation that every included component is production-ready.

Areas involving authentication, authorization, file-system access, container execution, external integrations, and sensitive data require appropriate security controls and testing before being exposed to untrusted users.

Secrets and credentials should be managed securely and must not be committed to source control. Any credentials that may have been exposed should be rotated.

The implementation and integration status of individual features may differ across the repository.

## 11. Project Ownership

LogicTree Academy is an independently developed project created by **Alikho Mnotoza**.

The repository is public for project visibility and technical review. Public availability should not be interpreted as permission to reproduce, redistribute, modify, or commercially exploit the source code.

Any applicable licence or separate written permission takes precedence over this statement.

## 12. Conclusion

LogicTree Academy represents an ongoing exploration of the intersection between education, software engineering, infrastructure, and artificial intelligence.

Through its Django backend, supporting services, developer-tool experiments, and CUBE-related work, the project investigates how different technical systems can contribute to a broader learning environment.

The emphasis is on practical implementation, engineering exploration, and the development of interconnected systems.

**LogicTree Academy — Coding · Maths · Physics.**
