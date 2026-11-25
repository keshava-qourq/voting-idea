# Planning

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### EPIC-001 · approved · source: plan:EPIC-001

Colleagues create an account with email and password, log in and log out. Passwords are stored hashed.

- Assumptions surfaced: any email may sign up; no email verification or password reset; only the email is kept as personal data.
- Sessions are stated as outcomes (expiry, ending on log out). The mechanism is not prescribed.
- Version noted in the plan: the cookie-session assumption was not made a requirement because the web pages and API may run on separate web addresses.
- Differs from the requirements-phase stack rationale, which mentions 'session-cookie login'. Both versions are recorded; the input does not resolve it.

**Related:** US-001, US-002, US-003, US-004

### EPIC-002 · approved · source: plan:EPIC-002

Anyone can view all ideas ranked by vote count, highest first. Ties are ordered newest first and every idea shows its count.

- Tie ordering is an assumption.
- No editing, deleting, comments or categories in this version.

**Related:** US-005, US-006, US-007

### EPIC-003 · approved · source: plan:EPIC-003

Logged-in users post an idea with a title and short description. Visitors who try to post are prompted to log in.

- Editing and deleting posted ideas is out of scope (assumption).

**Related:** US-008, US-009

### EPIC-004 · approved · source: plan:EPIC-004

Logged-in users upvote ideas, one vote per user per idea. Votes are permanent upvotes.

- No un-voting and no downvotes.
- Users may vote on their own ideas.
- Voting requires login.
- All assumptions confirmed as open.

**Related:** US-010, US-011, US-012

### EPIC-005 · approved · source: plan:EPIC-005

A responsive web app that works on desktop and mobile browsers.

- No native app.

**Related:** US-013

### EPIC-006 · approved · source: plan:EPIC-006

Accounts, ideas and votes are kept in a relational database. Only the email address is kept as personal data.

- No external services or API keys, no payments, and no specific regulation applies (general industry).
- Expected load is low: a few dozen trusted colleagues.
- Conflict: this epic says 'SQLite or Postgres', while the approved requirements fix PostgreSQL 16. Both are recorded; the approved requirements govern the stack.

**Related:** US-014, US-015

### EPIC-007 · approved · source: plan:EPIC-007

Basic documentation so the team can run and use the board.

- Any credential shown must be a placeholder in angle brackets.

**Related:** US-016
<!-- sdlc:auto:end narrative -->
