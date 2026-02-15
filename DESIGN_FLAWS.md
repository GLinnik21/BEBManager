# BEBManager Design Flaws Analysis

## Critical: Security

### 1. Permissive-by-default access control
**File:** `beb-manager/library/beb_lib/storage/access_validator.py:20-24`

```python
def _create_access_type(query: peewee.ModelSelect):
    if query.count() == 0:
        return AccessType.READ_WRITE  # No record = full access!
    else:
        return AccessType(query[0].access_type)
```

When no access record exists for a user, full `READ_WRITE` access is granted. The safe default should be `NONE`. Any user with no explicit access entry can read and write anything.

### 2. Hardcoded Django SECRET_KEY
**File:** `beb-manager/web_app/web_app/settings.py:23`

The secret key is hardcoded in source control. It's used for session tokens and CSRF protection. Anyone who reads the repo can forge sessions.

### 3. DEBUG=True with empty ALLOWED_HOSTS
**File:** `beb-manager/web_app/web_app/settings.py:26,28`

Exposes stack traces, settings, and internal paths to any user. Empty `ALLOWED_HOSTS` allows Host header injection.

### 4. EOL Django 1.11
The framework reached end-of-life in April 2020. Known security vulnerabilities are unpatched.

---

## Critical: Bugs

### 5. Wrong argument passed to `plan_read`
**File:** `beb-manager/library/beb_lib/model/model.py:243-247`

```python
for card in response.cards:
    try:
        card.plan = self.plan_read(card.user_id, request_user_id)  # BUG: should be card.unique_id
    except Error:
        pass
```

`plan_read(card_id, request_user_id)` expects a card ID, but `card.user_id` (the creator's user ID) is passed instead. Plans are looked up for the wrong card entirely. The `except Error: pass` silently hides the failure.

### 6. `create_cards_by_plans` mutates the original card ORM object
**File:** `beb-manager/library/beb_lib/storage/processors/plan_processor.py:21-35`

```python
card = plan.card
card.id = None      # Mutates the ORM model in memory
card.created = last_created_at
card.save()         # INSERT (because id=None), but original card's state is corrupted
```

Setting `card.id = None` on the fetched ORM model and calling `save()` creates a new row, but the original `plan.card` reference is corrupted. On the next loop iteration, `plan.card` may return the mutated object.

---

## Critical: Performance

### 7. N+1 queries in `_create_card_from_orm`
**File:** `beb-manager/library/beb_lib/storage/processors/card_processor.py:39-55`

```python
def _create_card_from_orm(card_model: CardModel) -> Card:
    for parent_child in ParentChild.select().where(ParentChild.parent == card_model):  # query per card
        children += [parent_child.child.id]
    for tag_card in TagCard.select().where(TagCard.card == card_model):  # query per card
        tags += [tag_card.tag.id]
    plan = PlanModel.get_or_none(PlanModel.card == card_model)  # query per card
```

Every card read triggers 3 additional queries. Listing 100 cards = 300+ queries. No prefetching or joins are used.

### 8. O(N) user iteration for access management
**File:** `beb-manager/web_app/beb_manager/views.py:109-113` (repeated at lines 244, 374, 463)

```python
for user in User.objects.all():
    if user not in can_read and can_read:
        MODEL.remove_right(board_id, Board, user.id, AccessType.READ)
    if user not in can_write and can_write:
        MODEL.remove_right(board_id, Board, user.id, AccessType.WRITE)
```

Iterates over every user in the system and makes individual DB calls for each. With 1000 users, this is 2000+ queries per edit operation. Copy-pasted across 4 view functions.

---

## High: Architecture

### 9. God Object — `Model` class
**File:** `beb-manager/library/beb_lib/model/model.py` (476 lines, 20+ public methods)

Handles CRUD for boards, lists, cards, tags, plans, access control, and convenience queries. Violates Single Responsibility Principle.

### 10. Global mutable state in web views
**File:** `beb-manager/web_app/beb_manager/views.py:21`

```python
MODEL = Model(settings.BEB_LIB_DATABASE_PATH)
```

A single `Model` instance is shared across all requests. Under concurrent requests (WSGI workers), this creates thread-safety issues with the shared Peewee database connection.

### 11. Class attributes mutated per-request
**File:** `beb-manager/web_app/beb_manager/views.py:53,161-162,277`

```python
Board.editable = True
Card.editable = True
CardsList.editable = True
```

These are class-level mutations. In a concurrent server, one request setting `Card.editable = True` affects all other in-flight requests. Race condition.

### 12. No transaction boundaries
**File:** `beb-manager/library/beb_lib/storage/processors/board_processor.py:76-84`

```python
def delete_board(request, user_id):
    BoardUserAccess.delete().where(BoardUserAccess.board == board).execute()
    for card_list in board.card_lists:
        list_processor._delete_list(card_list)
    board.delete_instance()
```

Multi-step deletions have no transaction wrapping. A failure mid-way leaves orphaned records.

### 13. Circular dependency resolved with late imports
**File:** `beb-manager/library/beb_lib/storage/provider.py:72-77`

```python
# To prevent import cycle
from beb_lib.storage.processors.board_processor import process_board_call
from beb_lib.storage.processors.card_processor import process_card_call
```

The comment explicitly acknowledges the circular dependency. Processors import from `provider.py` and `provider.py` imports from processors.

---

## Medium: Error Handling

### 14. Silent exception swallowing
**Files:** `model.py:246`, `plan_processor.py:34`, `views.py:73-74,532-533`

```python
except Error:
    pass
```

Errors are caught and silently discarded in at least 6 places. The `model.py:246` case is particularly harmful — it hides the bug from flaw #5 above.

### 15. Copy-pasted error translation block
**File:** `beb-manager/library/beb_lib/model/model.py` — repeated ~12 times

```python
if error is not None:
    if error.code == StorageProviderErrors.ACCESS_DENIED:
        raise AccessDeniedError(error.description)
    elif error.code == StorageProviderErrors.BOARD_DOES_NOT_EXIST:
        raise BoardDoesNotExistError(error.description)
    else:
        raise Error("""Undefined DB exception! ...""")
```

Should be a single helper or the storage layer should raise exceptions directly.

---

## Medium: API Design

### 16. Type dispatch on class name strings
**File:** `beb-manager/library/beb_lib/storage/access_validator.py:62-80`

```python
class_name = object_type.__name__
if class_name == Board.__name__:
    ...
elif class_name == CardsList.__name__:
    ...
```

Uses string comparison of class names instead of `isinstance` or polymorphism. Fragile and not extensible.

### 17. Non-unique request IDs via `random.randrange(1000000)`
**File:** `model.py:53,89,110,129,...` — used 15+ times

Request IDs have no uniqueness guarantee and are never used for correlation.

### 18. Tags have no access control
`TagDataRequest` uses `REQUEST_BASE_FIELDS` (no `request_user_id`), unlike all other request types. Any user can read/write/delete any tag.

---

## Medium: Testing

### 19. Minimal test coverage
Only basic storage provider operations are tested. No tests for: access control logic, `Model` mediator, web views, CLI, or error conditions.

---

## Low: Code Quality

### 20. Debug `print()` statements in views
**File:** `beb-manager/web_app/beb_manager/views.py:481,497`

### 21. Typo: `quarry` instead of `query`
**File:** `card_processor.py:71,77,112`

### 22. No dependency version pinning
`setup.py` files specify `install_requires=['peewee']` with no version constraints.
