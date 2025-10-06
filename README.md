# Taiga MCP Server

<div align="center">

**A production-ready Model Context Protocol (MCP) server for Taiga Project Management**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

[Getting Started](#-quick-start) • [Features](#-features) • [Tools](#-available-tools) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

Taiga MCP Server enables seamless integration between Large Language Models (LLMs) and [Taiga](https://taiga.io/) project management platform through the Model Context Protocol. Built with Python's async/await patterns and type-safe Pydantic models, it provides a robust, production-ready solution for AI-powered project management automation.

### Why Taiga MCP?

- **🤖 Natural Language Interface**: Interact with Taiga using conversational commands
- **🔄 Async-First**: Built on modern async/await for high performance
- **🛡️ Type-Safe**: Full Pydantic validation for reliability
- **🎯 Production Ready**: Comprehensive error handling and logging
- **🔌 Extensible**: Clean architecture for easy feature additions
- **📦 Zero Config**: Works out-of-the-box with Claude Desktop, Cursor, Windsurf

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Token-based auth with automatic refresh |
| 📊 **Project Management** | List, view, and search projects by ID or slug |
| 📝 **User Stories** | Full CRUD operations with pagination support |
| ✅ **Task Management** | Create and organize tasks within stories |
| 👥 **Team Collaboration** | View members and assign work |
| 🏷️ **Rich Metadata** | Tags, story points, due dates, custom fields |
| 🔍 **Flexible Queries** | Support for IDs, slugs, and reference numbers (#42) |

### Technical Features

- **Async Architecture**: Non-blocking I/O for optimal performance
- **Smart Caching**: Token management with auto-refresh
- **Intelligent Pagination**: Auto-fetch all or page-by-page
- **Optimistic Locking**: Version-based updates prevent conflicts
- **Role-Based Points**: Automatic detection and handling
- **Flexible Identifiers**: Use IDs, slugs, or #ref numbers interchangeably

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 or higher
- **Taiga Account**: taiga.io or self-hosted instance
- **MCP Client**: Claude Desktop, Cursor, Windsurf, or any MCP-compatible client

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/taiga-mcp.git
cd taiga-mcp

# Create virtual environment (or use conda)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Configure credentials
cp .env.example .env
nano .env  # Add your Taiga credentials
```

### Configuration

Create `.env` file:

```env
TAIGA_API_URL=https://api.taiga.io/api/v1
TAIGA_USERNAME=your_username
TAIGA_PASSWORD=your_password
DEBUG=false
```

**See [RUN.md](./RUN.md) for detailed setup instructions for Claude Desktop and Claude Code.**

---

## 🛠️ Available Tools

The server exposes 10 tools through the MCP protocol:

### Authentication

| Tool | Description | Parameters |
|------|-------------|------------|
| `authenticate` | Authenticate with Taiga API | `username` (optional), `password` (optional) |

### Project Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `listProjects` | List all accessible projects | None |
| `getProject` | Get project details | `projectIdentifier` (ID or slug) |
| `listProjectMembers` | List project team members | `projectIdentifier` |

### User Story Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `createUserStory` | Create a new user story | `projectIdentifier`, `subject`, `description`*, `status`*, `tags`* |
| `listUserStories` | List stories with pagination | `projectIdentifier`, `pageSize`*, `page`*, `fetchAll`* |
| `getUserStory` | Get story details | `userStoryIdentifier`, `projectIdentifier`* |
| `updateUserStory` | Update existing story | `userStoryIdentifier`, `projectIdentifier`*, `subject`*, `description`*, `status`*, `assignedTo`*, `tags`*, `points`*, `dueDate`* |

### Task Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `createTask` | Create task in story | `projectIdentifier`, `userStoryIdentifier`, `subject`, `description`*, `status`*, `tags`* |
| `listUserStoryTasks` | List tasks for a story | `userStoryIdentifier`, `projectIdentifier`* |

_* = optional parameter_

---

## 💬 Example Usage

Once configured with your LLM client, use natural language:

```
"List all my Taiga projects"

"Show me details about project 'mobile-app'"

"Create a user story in backend-api titled 'Implement OAuth2 authentication'
with description 'Add JWT-based OAuth2 flow for API endpoints'"

"List all user stories in the mobile-app project"

"Update user story #42 - set status to 'In Progress' and assign to john"

"Show me all tasks for user story #42"

"Create a task in story #42 titled 'Write unit tests for auth module'"
```

---

## 🏗️ Architecture

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Protocol** | [MCP 1.0](https://modelcontextprotocol.io/) | LLM-tool communication |
| **Language** | Python 3.10+ | Core implementation |
| **HTTP Client** | [httpx](https://www.python-httpx.org/) | Async Taiga API calls |
| **Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Type-safe data models |
| **Config** | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Environment management |
| **Testing** | [pytest](https://pytest.org/) + [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) | Test framework |

### Project Structure

```
taiga-mcp/
├── app/                          # Main application package
│   ├── core/                     # Core functionality
│   │   ├── auth.py              # Authentication & token management
│   │   ├── client.py            # Async HTTP client wrapper
│   │   └── exceptions.py        # Custom exception hierarchy
│   ├── models/                   # Pydantic data models
│   │   ├── project.py           # Project & member models
│   │   ├── userstory.py         # User story models
│   │   ├── task.py              # Task models
│   │   ├── user.py              # User models
│   │   └── status.py            # Status models
│   ├── services/                 # Business logic layer
│   │   ├── project_service.py   # Project operations
│   │   ├── userstory_service.py # User story operations
│   │   ├── task_service.py      # Task operations
│   │   └── user_service.py      # User operations
│   ├── config.py                 # Settings management
│   └── server.py                 # MCP server & tool definitions
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── pyproject.toml               # Project metadata & dependencies
├── README.md                    # This file
├── RUN.md                       # Setup & usage guide
└── .env.example                 # Example environment config
```

### Design Patterns

#### 1. **Async/Await Throughout**
All I/O operations use Python's `async/await` for non-blocking execution:

```python
async with TaigaClient() as client:
    projects = await project_service.list_projects()
```

#### 2. **Service Layer Pattern**
Business logic is encapsulated in service classes:

```python
class ProjectService:
    async def list_projects(self) -> list[Project]:
        data = await self.client.get("/projects")
        return [Project(**proj) for proj in data]
```

#### 3. **Pydantic Validation**
All data is validated using Pydantic models:

```python
class UserStory(BaseModel):
    id: int
    subject: str
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: Any) -> list[str]:
        # Handle both ['tag'] and [['tag', None]] formats
        ...
```

#### 4. **Error Handling**
Custom exception hierarchy for precise error handling:

```python
try:
    await client.get("/projects/123")
except ResourceNotFoundError as e:
    logger.error(f"Project not found: {e.identifier}")
except TaigaAPIError as e:
    logger.error(f"API error: {e.status_code}")
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type check
mypy app/
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_auth.py -v

# Integration tests (requires Taiga credentials)
pytest tests/integration/ -v

# With coverage report
pytest --cov=app --cov-report=term-missing
```

### Code Quality Tools

| Tool | Purpose | Command |
|------|---------|---------|
| **Black** | Code formatting | `black app/ tests/` |
| **Ruff** | Fast linting | `ruff check app/ tests/` |
| **Mypy** | Type checking | `mypy app/` |
| **Pytest** | Testing | `pytest` |

---

## 🗺️ Roadmap

### Phase 1: Core Features ✅
- [x] Authentication & token management
- [x] Project listing and details
- [x] User story CRUD operations
- [x] Task management
- [x] Team member listing
- [x] Smart pagination
- [x] Flexible identifiers (ID/slug/#ref)

### Phase 2: Enhanced Features 🚧
- [ ] Caching layer (Redis/in-memory)
- [ ] Rate limiting
- [ ] Bulk operations
- [ ] Epic support
- [ ] Sprint/Milestone management
- [ ] Issues/Bugs tracking
- [ ] Wiki page integration
- [ ] File attachments
- [ ] Comments on stories/tasks
- [ ] Custom field support
- [ ] Activity history tracking

### Phase 3: Advanced Features 🎯
- [ ] Standalone CLI tool
- [ ] Analytics & reporting
- [ ] Data export/import
- [ ] Webhook support
- [ ] Notification integrations (Slack, Email)
- [ ] Project templates
- [ ] Burndown charts
- [ ] Time tracking

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests**: Ensure coverage for new code
5. **Run quality checks**:
   ```bash
   black app/ tests/
   ruff check app/ tests/
   mypy app/
   pytest
   ```
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

- Follow existing code style (Black formatting)
- Add type hints to all functions
- Write docstrings for public APIs
- Include tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the The GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - For the excellent LLM-tool integration standard
- **[Taiga](https://taiga.io/)** - For the powerful open-source project management platform
- **[Anthropic](https://www.anthropic.com/)** - For Claude and MCP SDK
- **Community Contributors** - For feedback and improvements

---

## 📞 Support

- **Documentation**: [RUN.md](./RUN.md) for setup guides
- **Issues**: [GitHub Issues](https://github.com/yourusername/taiga-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/taiga-mcp/discussions)
- **Taiga API Docs**: [https://docs.taiga.io/api.html](https://docs.taiga.io/api.html)

---

<div align="center">

**Built with ❤️ for the AI-powered project management community**

⭐ Star this repo if you find it useful!

</div>

---

## ⚠️ Disclaimer

This project is not officially affiliated with Taiga. It's a community-driven MCP server implementation for integrating Taiga with LLM applications.
