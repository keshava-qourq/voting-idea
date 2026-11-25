# Planning

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
### EPIC-001 · approved · source: plan:EPIC-001

Colleagues create an account with email and password, log in and log out. Passwords are stored hashed.

- Goal: account creation, log in and log out.
- Assumptions surfaced:
  - Any email address may sign up (no company-domain restriction).
  - No email verification and no password reset in this version.
  - The only personal data kept is the email address.
  - Passwords are stored hashed.
- Sessions are stated as outcomes (expiry, ending on log out). The mechanism is not prescribed.
- Cookie-based sessions were a confirmed assumption but are not made a requirement. The web pages and API run on separate web addresses, where cookies are not sent between them.
- Plan: 4 stories, 14 points, all assigned to backend-agent.

**Related:** US-001, US-002, US-003, US-004

### EPIC-002 · approved · source: plan:EPIC-002

Anyone, logged in or not, can view all ideas ranked by vote count, highest first. Every idea shows its vote count.

- Goal: a public board ranked by votes.
- Assumption: ties are ordered newest first.
- Ideas cannot be edited or deleted in this version.
- No comments or categories in this version.
- Plan: 3 stories, 8 points. Backend-agent has 6 points and frontend-agent has 2.

**Related:** US-005, US-006, US-007

### EPIC-003 · approved · source: plan:EPIC-003

Logged-in users post an idea consisting of a title and a short description. Visitors who try to post are prompted to log in.

- Goal: idea posting for logged-in users.
- Assumption: editing and deleting posted ideas is out of scope.
- Plan: 2 stories, 8 points. Backend-agent has 5 points and frontend-agent has 3.

**Related:** US-008, US-009

### EPIC-004 · approved · source: plan:EPIC-004

Logged-in users upvote ideas, with one vote per user per idea. Votes are permanent upvotes.

- Goal: upvoting with a fair, one-vote-per-user-per-idea ranking.
- Assumptions, all recorded in the input as confirmed:
  - No un-voting and no downvotes.
  - Users may vote on their own ideas.
  - Voting requires login.
- Plan: 3 stories, 10 points. Backend-agent has 8 points and frontend-agent has 2.

**Related:** US-010, US-011, US-012

### EPIC-005 · approved · source: plan:EPIC-005

The app is a responsive web app for desktop and mobile browsers. There is no native app.

- Goal: responsive layout across desktop and mobile browsers.
- Out of scope: native app.
- Plan: 1 story, 5 points, assigned to frontend-agent.

**Related:** US-013

### EPIC-006 · approved · source: plan:EPIC-006

Accounts, ideas and votes are kept in a simple relational database behind a standard full-stack web framework. No external services are needed.

- Goal: persistent storage and minimal personal data.
- Storage: SQLite or Postgres.
- No external services or API keys, and no payments.
- No specific regulation applies (general industry).
- Only the email address is kept as personal data.
- Expected load is low: a few dozen trusted colleagues.
- Plan: 2 stories, 6 points, all assigned to backend-agent.

**Related:** US-014, US-015

### EPIC-007 · approved · source: plan:EPIC-007

Basic documentation so the team can run and use the board.

- Goal: setup and usage documentation.
- Constraint: any credential shown must be a placeholder in angle brackets.
- Plan: 1 story, 2 points, assigned to devops-agent.

**Related:** US-016

### SPRINT-1 · approved · source: plan:SPRINT-1

Sprint 1 lays the foundation: persistent schema, secure password storage, sign up, log in and log out. Capacity is 20.

- Goal: Foundation: persistent schema, secure password storage, sign up, log in and log out.
- Capacity: 20.
- Plan version 1 (approved).
- The input does not say which stories are assigned to this sprint.

### SPRINT-2 · approved · source: plan:SPRINT-2

Sprint 2 delivers the core loop: public ranked board, posting ideas and upvoting. Capacity is 20.

- Goal: Core loop: public ranked board, posting ideas and upvoting.
- Capacity: 20.
- Plan version 1 (approved).
- The input does not say which stories are assigned to this sprint.

### SPRINT-3 · approved · source: plan:SPRINT-3

Sprint 3 covers visitor log-in prompts, one-vote UX, responsive layout and documentation. Capacity is 20.

- Goal: Visitor log-in prompts, one-vote UX, responsive layout and documentation.
- Capacity: 20.
- Plan version 1 (approved).
- The input does not say which stories are assigned to this sprint.
<!-- sdlc:auto:end narrative -->
