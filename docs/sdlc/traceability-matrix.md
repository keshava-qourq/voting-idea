# Traceability Matrix

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start legend -->
Built from recorded links, not written by a model: requirement key → plan item (`source_stable_key`) → development ticket (`stable_key`) → the ticket's test steps → the last live deployment that started after the work finished. **AC tests** counts the story's acceptance criteria that have a test case, and those whose test cases all passed in the latest finished E2E run. **Tests** counts the tests written for the story, and **Result** how many last passed, how many failed and when, as of this page's generation; the Documentation tab shows them live.
<!-- sdlc:auto:end legend -->

<!-- sdlc:auto:start matrix -->
| Requirement | Epic | Title | Plan items | Sprint | Design | Code | Commits | Ticket | Test step | Tests | Result | AC tests | Deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US-001 | EPIC-001 | Sign up with email and password | US-001 | 1 | POST /auth/signup, api_auth, db, sessions, spa, users | backend/alembic/versions/0002_unique_email_ignoring_case.py, backend/app/auth.py, backend/app/errors.py, backend/app/main.py, backend/app/routers/auth.py +17 more | 9ef4184 | delivered | succeeded | 0 | No tests | 0/5 tested · 0/5 passing | 7b595a468c04 |
| US-002 | EPIC-001 | Passwords are stored securely | US-002 | 1 | api_auth, db, users | backend/tests/integration/test_us002_password_storage.py, backend/tests/unit/test_password_hashing.py, backend/tests/unit/test_password_not_exposed.py | 1d8f440 | delivered | succeeded | 0 | No tests | 0/2 tested · 0/2 passing | 7b595a468c04 |
| US-003 | EPIC-001 | Log in | US-003 | 1 | GET /auth/me, POST /auth/login, api_auth, db, sessions, spa, users | backend/alembic/versions/0003_sessions.py, backend/app/auth.py, backend/app/errors.py, backend/app/main.py, backend/app/models.py +8 more | d30ebc4 | delivered | failed | 0 | No tests | 0/4 tested · 0/4 passing | 7b595a468c04 |
| US-004 | EPIC-001 | Log out | US-004 | 1 | POST /auth/logout, api_auth, sessions, spa | backend/app/auth.py, backend/app/routers/auth.py, backend/app/schemas.py, backend/tests/unit/test_logout.py, frontend/src/App.tsx +4 more | 67d431d | delivered | failed | 0 | No tests | 0/2 tested · 0/2 passing | 7b595a468c04 |
| US-005 | EPIC-002 | View ideas ranked by votes without logging in | US-005 | 2 | GET /ideas, api_board, db, ideas, spa, votes | — | — | not started | not run | 0 | No tests | 0/3 tested · 0/3 passing | — |
| US-006 | EPIC-002 | Order tied ideas newest first | US-006 | 2 | GET /ideas, api_board, ideas, votes | — | — | not started | not run | 0 | No tests | 0/2 tested · 0/2 passing | — |
| US-007 | EPIC-002 | See the vote count on every idea | US-007 | 2 | GET /ideas, ideas, spa | — | — | not started | not run | 0 | No tests | 0/2 tested · 0/2 passing | — |
| US-008 | EPIC-003 | Post an idea | US-008 | 2 | POST /ideas, api_board, db, ideas, spa, users | — | — | not started | not run | 0 | No tests | 0/4 tested · 0/4 passing | — |
| US-009 | EPIC-003 | Prompt visitors to log in when posting | US-009 | 3 | GET /auth/me, POST /ideas, spa | — | — | not started | not run | 0 | No tests | 0/2 tested · 0/2 passing | — |
| US-010 | EPIC-004 | Upvote an idea | US-010 | 2 | POST /ideas/{idea_id}/vote, api_board, db, ideas, spa, votes | — | — | not started | not run | 0 | No tests | 0/3 tested · 0/3 passing | — |
| US-011 | EPIC-004 | Limit to one vote per user per idea | US-011 | 3 | GET /ideas, POST /ideas/{idea_id}/vote, api_board, db, spa, votes | — | — | not started | not run | 0 | No tests | 0/3 tested · 0/3 passing | — |
| US-012 | EPIC-004 | Prompt visitors to log in when voting | US-012 | 3 | POST /ideas/{idea_id}/vote, spa | — | — | not started | not run | 0 | No tests | 0/2 tested · 0/2 passing | — |
| US-013 | EPIC-005 | Use the board on desktop and mobile browsers | US-013 | 3 | spa | — | — | not started | not run | 0 | No tests | 0/3 tested · 0/3 passing | — |
| US-014 | EPIC-006 | Keep accounts, ideas and votes | US-014 | 1 | db, ideas, sessions, users, votes | backend/alembic/versions/0002_unique_vote_per_user_idea.py, backend/app/models.py, backend/tests/integration/test_us014_keep_data.py, backend/tests/unit/test_no_external_services.py, backend/tests/unit/test_persistence.py | c724007 | delivered | succeeded | 0 | No tests | 0/3 tested · 0/3 passing | 7b595a468c04 |
| US-015 | EPIC-006 | Keep personal data minimal | US-015 | 2 | api_auth, api_board, users | — | — | not started | not run | 0 | No tests | 0/2 tested · 0/2 passing | — |
| US-016 | EPIC-007 | Setup and usage guide | US-016 | 3 | — | — | — | not started | not run | 0 | No tests | 0/3 tested · 0/3 passing | — |
<!-- sdlc:auto:end matrix -->
