# BEBManager Architecture

## Overview

BEBManager is a task tracker / project management system (similar to Trello/Jira) written in Python. It lets users create boards, organize tasks into lists, assign cards, apply tags, and manage access control. The project is split into three independent packages that form a layered architecture:

```
┌──────────────────────────────────────────────────────────┐
│               Presentation Layer                         │
│  ┌─────────────────────┐  ┌────────────────────────────┐ │
│  │  CLI (console/)     │  │  Web App (web_app/)        │ │
│  │  argparse-based     │  │  Django 1.11 + Bootstrap 4 │ │
│  └────────┬────────────┘  └──────────┬─────────────────┘ │
└───────────┼──────────────────────────┼───────────────────┘
            │                          │
┌───────────┴──────────────────────────┴───────────────────┐
│              Core Library (beb_lib/)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Domain       │  │ Model        │  │ Storage        │  │
│  │ Entities     │  │ (Mediator)   │  │ Provider       │  │
│  └──────────────┘  └──────────────┘  └───────┬────────┘  │
│                                              │           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────┴────────┐  │
│  │ Access       │  │ Request/     │  │ Processors     │  │
│  │ Validator    │  │ Response DTOs│  │ (per entity)   │  │
│  └──────────────┘  └──────────────┘  └───────┬────────┘  │
└──────────────────────────────────────────────┼───────────┘
                                               │
┌──────────────────────────────────────────────┴───────────┐
│              Persistence (Peewee ORM → SQLite)           │
└──────────────────────────────────────────────────────────┘
```

## Three Packages

| Package | Location | Purpose |
|---|---|---|
| **beb_lib** | `beb-manager/library/` | Core library — domain entities, business logic, storage, access control |
| **beb-manager CLI** | `beb-manager/console/` | Command-line interface using argparse |
| **Web App** | `beb-manager/web_app/` | Django web interface with Bootstrap 4 templates |

Both the CLI and web app depend on `beb_lib` but are otherwise independent. This separation means the core logic is reusable and UI-agnostic.

## Domain Model

The core entities live in `beb_lib/domain_entities/`:

```
Board
 └── CardsList (1:N)
      └── Card (1:N)
           ├── children: Card[] (parent-child hierarchy)
           ├── tags: Tag[] (many-to-many)
           ├── priority: LOW(1) / MEDIUM(50) / HIGH(100)
           ├── assignee_id, user_id
           ├── expiration_date
           └── plan: Plan (optional, for recurring tasks)

Tag (name, color)
Plan (card_id, interval, last_created_at)
```

All entities inherit from `UniqueObject` which provides a unique ID.

## Request Flow (Provider/Processor Pattern)

The system uses a Request → Provider → Processor pipeline:

1. **UI layer** (CLI `app.py` or Django `views.py`) constructs a domain entity and calls a method on `Model` (`beb_lib/model/model.py`).
2. **Model** (mediator) creates a typed `*DataRequest` named tuple (e.g., `CardDataRequest` with `request_type=WRITE`).
3. **StorageProvider** (`beb_lib/storage/provider.py`) receives the request and routes it via a handler map to the appropriate **Processor**.
4. **Processors** (`beb_lib/storage/processors/`) — one per entity type (`board_processor`, `card_processor`, `list_processor`, `tag_processor`, `plan_processor`) — each with a `METHOD_MAP` routing `RequestType` (READ/WRITE/DELETE) to handler functions.
5. Processors validate access, perform ORM operations, and return `*DataResponse` tuples or errors.

### Example: Creating a Card

```
CLI: beb-manager card add "Buy milk" -ln "To Do" -p high
 │
 ▼
Parser extracts: name="Buy milk", list_name="To Do", priority="high"
 │
 ▼
App.add_card() → creates Card(name, priority=100)
 │
 ▼
Model.card_write() → creates CardDataRequest(request_type=WRITE)
 │
 ▼
StorageProvider.execute() → routes to card_processor.process_card_call()
 │
 ▼
CardProcessor.write_card():
  - Validates user has WRITE access to list
  - Converts Card domain entity to CardModel
  - Saves CardModel to database
  - Returns CardDataResponse
 │
 ▼
App displays success message
```

## Access Control

Hierarchical, fine-grained permissions at three levels:

```
BoardUserAccess → CardListUserAccess → CardUserAccess
```

Access types are `READ`, `WRITE`, `READ_WRITE`, or `NONE`. The `access_validator.py` module checks permissions at each level — a user needs access at all levels to operate on a card. Access modes in the CLI use notation like `+rw`, `+r`, `+w`, `~rw`.

## Persistence

- **ORM**: Peewee (lightweight, framework-independent — chosen over Django ORM so the library doesn't depend on Django).
- **Database**: SQLite via Peewee's `DatabaseProxy` pattern for dynamic initialization.
- **ORM models** in `beb_lib/storage/models.py`: `BoardModel`, `CardListModel`, `CardModel`, `TagModel`, `PlanModel`, plus junction tables (`ParentChild`, `TagCard`) and access tables (`BoardUserAccess`, `CardListUserAccess`, `CardUserAccess`).

## User Management

Each UI manages users independently:

- **CLI**: Custom `UserProvider` with its own SQLite database (`cli-beb-manager.db`), decorators `@check_authorization` and `@check_board`.
- **Web**: Django's built-in `User` model with `@login_required`, plus a custom signup view.

The library itself only references users by ID, staying agnostic to authentication.

## Key Design Decisions

1. **Library independence** — `beb_lib` has no Django dependency; Peewee was chosen specifically for this.
2. **Named tuples as DTOs** — Request/response objects are immutable named tuples, not classes.
3. **Archived list pattern** — A system-wide "Archived" list is auto-created and protected from deletion; cards are archived rather than hard-deleted.
4. **Periodic tasks** — `Plan` entities with intervals trigger card creation via `trigger_card_plan_creation()`, automatically invoked on model operations (via `@process_plans` decorator in the web app).
5. **Separate databases** — The CLI app uses two SQLite databases: one for library data, one for CLI user/session data.
6. **Error handling** — `(response, error)` tuple returns throughout the storage layer, with enum-based error codes.

## Directory Structure

```
beb-manager/
├── library/                          # Core library package
│   ├── beb_lib/
│   │   ├── domain_entities/          # Pure domain models
│   │   │   ├── board.py
│   │   │   ├── cards_list.py
│   │   │   ├── card.py
│   │   │   ├── tag.py
│   │   │   ├── plan.py
│   │   │   └── unique_object.py
│   │   ├── model/
│   │   │   └── model.py              # Main mediator between UI and storage
│   │   ├── storage/
│   │   │   ├── provider.py           # StorageProvider (request routing)
│   │   │   ├── models.py             # Peewee ORM models
│   │   │   ├── access_validator.py   # Permission checking
│   │   │   ├── processors/           # Business logic per entity
│   │   │   │   ├── board_processor.py
│   │   │   │   ├── card_processor.py
│   │   │   │   ├── list_processor.py
│   │   │   │   ├── tag_processor.py
│   │   │   │   └── plan_processor.py
│   │   │   ├── provider_requests.py  # Request DTOs
│   │   │   └── provider_responses.py # Response DTOs
│   │   ├── provider_interfaces.py    # IProvider, IStorageProviderProtocol
│   │   └── logger.py
│   ├── tests/
│   └── setup.py
├── console/                          # CLI package
│   ├── beb_manager_cli/
│   │   ├── application/
│   │   │   ├── main.py               # Entry point
│   │   │   ├── app.py                # Main CLI app class
│   │   │   ├── parser.py             # Argument parsing
│   │   │   └── config.py
│   │   └── storage/
│   │       └── user_provider.py
│   └── setup.py
└── web_app/                          # Django web package
    ├── web_app/
    │   ├── settings.py
    │   └── urls.py
    ├── beb_manager/
    │   ├── views.py
    │   ├── urls.py
    │   ├── forms.py
    │   └── templates/
    └── manage.py
```
