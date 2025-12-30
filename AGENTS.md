# AGENTS.md

## Build/Lint/Test Commands

### Package Management

- **Install dependencies**: `uv sync`
- **Run the bot**: `uv run python main.py`

### Code Quality

- **Format code**: `uv run black .` (line-length: 88)
- **Sort imports**: `uv run isort .` (profile: black)
- **Lint**: `uv run pylint src/`
- **Type check**: `uv run pyright src/` (currently disabled in config)

### Testing

- **Run all tests**: `uv run pytest` (if pytest is added)
- **Run single test**: `uv run pytest tests/test_module.py::test_function` (when tests exist)

## Code Style Guidelines

### Imports

- Use isort with 5 sections: FUTURE, STDLIB, THIRDPARTY, FIRSTPARTY, LOCALFOLDER
- Import individual modules explicitly: `from sqlalchemy import String`, not `import sqlalchemy`
- Standard library imports: os, zoneinfo, typing, datetime
- Third-party: dotenv, telegram, sqlalchemy, jinja2
- Local modules: from src.\*

### Formatting

- Black formatter with 88 character line length
- Use f-strings for string formatting (interpolation enabled)
- Use double quotes for strings

### Type Hints

- Modern Python type hints with `|` union syntax: `User | None`, `str | None`
- Use `Mapped[T]` for SQLAlchemy ORM fields: `Mapped[int] = mapped_column(primary_key=True)`
- Annotate all function parameters and return types
- Type checking currently disabled (pyright typeCheckingMode = "off")

### Naming Conventions

- **Classes**: PascalCase (User, Scenario, BaseModel, ReminderStrategy)
- **Functions/Variables**: snake_case (get_user_by_chat, user_scenario)
- **Constants**: UPPER_CASE (CMD, UDK, END)
- **Private members**: underscore prefix when needed
- **Enums**: PascalCase with `auto()` values (class Menu(IntEnum))

### Handler Pattern

- Use factory functions: `build_*_handler()` returning handler objects
- Create conversation handlers via `build_conversation_handler()`
- Register handlers with `register(app: Application)` function
- Handlers are async functions with signature: `async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int`
- Return conversation states or END (-1)

### Database Patterns

- Use SQLAlchemy 2.0 ORM with declarative base
- BaseModel extends DeclarativeBase with `save()` method
- Relationships use `lazy="joined"` for eager loading
- Use `Session(engine)` context managers
- Use `Select(T).where(condition)` for queries
- Fetch with `s.scalars(selector).one_or_none()` or `.all()`

### Error Handling

- Try/except ValueError for type conversions (float(), int())
- Check for None before accessing properties
- Use fallback handlers in ConversationHandler: cancel_handler, unexpected_err_handler
- Return conversation state on validation failure to retry input

### Conversation States

- Define states as IntEnum classes: `class Menu(IntEnum)`
- Use auto() for automatic integer values
- Global END = -1 for conversation termination
- Use map_to_parent for nested conversation handlers

### User Data Keys

- Define keys as IntEnum: `class UDK(IntEnum)` with auto()
- Store in context.user_data during multi-step conversations

### Keyboards

- Functions return InlineKeyboardMarkup objects
- Use batched() for grid layouts (3 columns typical)
- Include navigation buttons (Back, etc.) in keyboard

### Environment

- Use python-dotenv for configuration
- Required env vars: BOT_TOKEN, DB_URL, TEMPLATES_FOLDER
- Template rendering with Jinja2 from static/templates/

### Async/Await

- All handler functions must be async
- Use `await` for telegram operations (reply_text, edit_message_text)
- Database operations are synchronous (no async SQLAlchemy)

### Comments

- Keep minimal inline comments
- Use # pylint: disable for specific pylint warnings (e.g., E1136)
- No docstrings required (disabled in pylint config)

### GIT

- Do not make commits, till user ask u directly.
- All commit messages should follow "Conventional Commits" strategy.

### Messages

- All bot messages should be on English.
