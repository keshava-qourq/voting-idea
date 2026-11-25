# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-STACK · approved · source: requirements:technology-stack

The product owner approved a fixed technology stack. Design must use exactly these technologies, with no substitutions.

- Backend: FastAPI 0.115
  - Small API covering sign up, log in, log out, list ideas, post an idea and upvote.
  - Passwords hashed.
  - One-vote-per-user-per-idea rule also enforced in the database.
- Frontend: React 19
  - Re-ordering ideas list, sign-up/login form and post-idea form.
  - Works on desktop and mobile browsers.
  - No heavy framework features needed.
- Database: PostgreSQL 16
  - Three plain tables: users, ideas, votes.
  - Uniqueness rule on user + idea guarantees one vote per person per idea.
  - Order by vote count, then newest first.
- Cloud: AWS
  - One small server plus a managed Postgres database.
  - No external services, queues or file storage.

Conflicting statements in the input (both recorded, none chosen):
- Backend rationale describes 'session-cookie login'. The planning notes say the session mechanism is deliberately not prescribed, and that cookies are not assumed because the web pages and API may run on separate web addresses.
- The planning notes describe the database as 'SQLite or Postgres'. The approved requirements fix PostgreSQL 16.

**Related:** REQ-SERVICES, NFR-009

### REQ-SERVICES · approved · source: requirements:services

The app runs from one small AWS server plus a managed PostgreSQL database. It needs no other external services.

- Hosting: AWS, the only cloud option offered. One small server.
- Data store: managed PostgreSQL 16 holding accounts, ideas and votes.
- Not needed: external services, queues, file storage, payment provider, API keys.
- Expected monthly cost: modest.
- Expected load: low, a few dozen trusted colleagues.

**Related:** REQ-STACK, NFR-009, NFR-007

### REQ-SCOPE · approved · source: requirements:scope

Lightweight delivery of an idea voting board with sign-up, posting, ranked listing and one-vote-per-idea upvoting. Editing, deleting, comments and account recovery are excluded.

Delivery scope: lightweight. Requirements version: 1.

In scope:
- Sign up with email and password.
- Log in and log out.
- Public ideas board ranked by vote count, highest first.
- Newest-first ordering for ideas with tied votes.
- Idea posting form (title and short description) for logged-in users.
- Upvoting ideas, one vote per user per idea.
- Vote count shown on every idea.
- Prompt to log in when a visitor tries to post or vote.
- Responsive layout for desktop and mobile browsers.
- Stored accounts, ideas and votes.
- Basic setup and usage documentation.

Scope decisions / out of scope:
- Voting requires login.
- Votes are permanent upvotes: no un-voting, no downvotes.
- Users may vote on their own ideas.
- No editing or deleting of ideas, no comments, no categories.
- No email verification or password reset.
- Any email address may sign up, with no company-domain restriction.
- Only the email address is kept as personal data.

**Related:** NFR-011, NFR-012

### REQ-FR-ACCOUNTS · approved · source: requirements:functional:sign-in-and-accounts

Visitors can sign up, log in and log out with email and password. Passwords are protected and login errors are generic.

- Sign up:
  - Visitor creates an account with email and password and is logged in straight away.
  - Duplicate emails (ignoring letter case), bad email formats and empty passwords are rejected with a clear message.
  - Any email domain is accepted. No email check is needed.
- Log in:
  - Registered user logs in with email and password. The screen shows they are logged in.
  - A wrong password or unknown email gives one generic message.
  - No password reset option.
- Log out:
  - A logged-in user can log out and then sees the board as a visitor.
  - After that, posting and voting are refused and the user is asked to log in.
- Protected passwords:
  - Passwords are kept only in a protected, salted form and are never shown or logged.
  - Only email and password are collected at sign-up.

**Related:** NFR-001, NFR-002, NFR-003, NFR-006, NFR-012

### REQ-FR-BOARD · approved · source: requirements:functional:ideas-board

Anyone can view all ideas ranked by votes, highest first, with ties broken newest first. Each idea shows its title, description and vote count.

- View ranked ideas:
  - Anyone, logged in or not, sees all ideas with the highest vote count first.
  - Reloading the board shows each idea in the place its current count earns.
  - With no ideas, a message invites people to post the first one.
- Newest first on ties: ideas with the same vote count are ordered newest first.
- Idea details and counts:
  - Each idea shows title, short description and vote count, including zero.
  - No edit, delete, comment or category controls appear.
  - Other users' email addresses are not shown.

**Related:** NFR-006

### REQ-FR-POSTING · approved · source: requirements:functional:posting-ideas

Logged-in users post an idea with a title and short description. Visitors are prompted to log in instead.

- Post an idea:
  - A logged-in user submits a title and short description. The idea appears on the board with zero votes.
  - Empty fields or text over the stated length limit are rejected with a message saying what to fix.
  - Ideas cannot be edited or deleted afterwards.
- Log-in prompt for posting:
  - A visitor who tries to open the post form or submit an idea is prompted to log in or sign up. No idea is created.
  - After logging in they return to the board or post form.

**Related:** NFR-004

### REQ-FR-VOTING · approved · source: requirements:functional:voting

Logged-in users upvote ideas, once per idea. Visitors who try to vote are prompted to log in.

- Upvote an idea:
  - A logged-in user upvotes an idea. Its count goes up by one and the board order updates.
  - Users may vote on their own ideas.
  - Votes are permanent: no un-voting, no downvotes.
- One vote per idea:
  - Each user gets one vote per idea.
  - Ideas already voted on show that status, and the vote control is disabled or replaced.
  - Repeat votes (double-clicks, a second tab) change nothing.
  - Voting on a different idea is still allowed.
- Log-in prompt for voting:
  - A visitor sees vote counts and vote controls on the board.
  - Using a vote control prompts them to log in or sign up. No vote is recorded.

**Related:** NFR-004, NFR-005

### REQ-FR-ACROSS · approved · source: requirements:functional:across-the-app

The app works on phone and desktop screens and keeps all data permanently. It needs no external service.

- Phone and desktop layout:
  - Board, sign-up, log-in and post forms work on phone-sized and desktop screens in current major browsers.
  - No sideways scrolling on a phone.
- Saved accounts, ideas and votes:
  - Stored permanently and still present after a restart.
  - No external service, payment provider or API key needed.

**Related:** NFR-007, NFR-008, NFR-009

### REQ-FR-GUIDE · approved · source: requirements:functional:guide

A short guide explains how to set up and start the app and how to use it. It states the known limits.

- Explains how to set up and start the app.
- Explains how to sign up, log in, post and upvote.
- States the limits: no editing, deleting, un-voting, password reset or email verification.
- Any secrets appear only as placeholders.

**Related:** NFR-009, NFR-010

### NFR-001 · approved · source: requirements:NFR-001

Security: passwords are stored only as salted hashes.

- Passwords are never stored as readable text.
- No password is shown on any page or message.
- No password is written to any log in readable form.

**Related:** REQ-FR-ACCOUNTS

### NFR-002 · approved · source: requirements:NFR-002

Security: sessions expire after a set lifetime and end immediately on log out.

- A session ends after a set session lifetime. The user must then log in again before posting or voting.
- Logging out ends the session straight away.
- After logout, posting or voting is refused even if the user presses the browser's back button.
- The session lifetime value is not stated in the input.

**Related:** REQ-FR-ACCOUNTS

### NFR-003 · approved · source: requirements:NFR-003

Security: login failures give the same message for an unknown email or a wrong password.

- The failure message is identical in both cases.
- This avoids revealing which accounts exist.

**Related:** REQ-FR-ACCOUNTS

### NFR-004 · approved · source: requirements:NFR-004

Security: the server refuses to create ideas or record votes unless the user is logged in.

- Enforced on the server side.
- Hiding the controls on screen is not sufficient.

**Related:** REQ-FR-POSTING, REQ-FR-VOTING

### NFR-005 · approved · source: requirements:NFR-005

Security: one vote per user per idea is enforced in the stored data as well as in the app.

- A user can have at most one vote on any idea.
- Enforced in the data layer and in the app.
- Double-clicks, repeated requests and a second browser tab never create a duplicate vote or change the count.

**Related:** REQ-FR-VOTING, REQ-STACK

### NFR-006 · approved · source: requirements:NFR-006

Privacy: only the email address (plus the hashed password) is collected and stored.

- No other personal data is collected.
- Other users' email addresses are not shown on the board.

**Related:** REQ-FR-BOARD, REQ-FR-ACCOUNTS

### NFR-007 · approved · source: requirements:NFR-007

Availability: accounts, ideas and votes survive restarts.

- Data is kept in permanent storage.
- After a restart, all data is still present and the board shows the same ranking.

**Related:** REQ-FR-ACROSS

### NFR-008 · approved · source: requirements:NFR-008

Compatibility: sign up, log in, posting and voting work on current major desktop and mobile browsers.

- Target: phone screen width around 360 pixels.
- On a phone-sized screen, content fits without horizontal scrolling and controls are easy to tap.
- On desktop, the layout stays readable.

**Related:** REQ-FR-ACROSS

### NFR-009 · approved · source: requirements:NFR-009

Maintainability: the app runs with no external service, payment provider or API key.

- The team can start the app from the project files and the setup guide alone.

**Related:** REQ-SERVICES, REQ-FR-ACROSS

### NFR-010 · approved · source: requirements:NFR-010

Maintainability: the guide shows secrets and configuration values only as placeholders.

- Placeholders are written in angle brackets.
- No real-looking values appear in the guide.

**Related:** REQ-FR-GUIDE

### NFR-011 · approved · source: requirements:NFR-011

Scalability (accepted risk): low load is accepted and no scaling work is planned.

- Built for a few dozen trusted colleagues with low traffic.
- No capacity planning or large-scale performance work in this version.

**Related:** REQ-SCOPE

### NFR-012 · approved · source: requirements:NFR-012

Security (accepted risk): no email verification and no password reset in this version.

- Any email address may sign up, with no company-domain restriction.
- This was a deliberate decision.

**Related:** REQ-SCOPE, REQ-FR-ACCOUNTS
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start summary -->
**Requirements version:** v1  
**Delivery scope:** lightweight  
**Approved:** 2026-11-25

**Capabilities in scope:** Sign up with email and password, Log in and log out, Public ideas board ranked by vote count, highest first, Newest-first ordering for ideas with tied votes, Idea posting form (title and short description) for logged-in users, Upvoting ideas, one vote per user per idea, Vote count shown on every idea, Prompt to log in when a visitor tries to post or vote, Responsive layout for desktop and mobile browsers, Stored accounts, ideas and votes, Basic setup and usage documentation, Voting requires login, Votes are permanent upvotes, with no un-voting or downvotes, Users may vote on their own ideas, No editing or deleting of ideas, no comments, no categories, No email verification or password reset, Any email address may sign up, with no company-domain restriction, Only the email address is kept as personal data

**Approved technology stack:**

| Layer | Choice | Rationale |
|---|---|---|
| backend | FastAPI | You asked for a standard full-stack web framework with session-cookie login and hashed passwords. FastAPI covers that with a small API: sign up, log in, log out, list ideas, post an idea and upvote. The one-vote-per-user-per-idea rule is enforced in the database too, so it holds even if the app code has a bug. |
| cloud | AWS | It is the only cloud option offered, and a small app like this runs on one small server plus a managed Postgres database. It needs no external services, queues or file storage. Monthly cost will be modest. |
| database | PostgreSQL | You wanted a simple relational database. Users, ideas and votes are three plain tables, and a uniqueness rule on user plus idea guarantees one vote per person per idea. Ordering by vote count then newest first is a straightforward query. Postgres was named as an acceptable option in the assumptions. |
| frontend | React | The board needs a list that re-orders as votes come in, a sign-up/login form and a post-idea form, all working on desktop and mobile browsers. React handles this well and is the only frontend option offered here. The visitor-facing list stays simple, so no heavy framework features are needed. |
<!-- sdlc:auto:end summary -->

<!-- sdlc:auto:start epics -->
## EPIC-001: Accounts and sign-in

Colleagues create an account with email and password, log in and log out. Assumptions surfaced: any email address may sign up (no company-domain restriction); there is no email verification and no password reset in this version; the only personal data kept is the email address. Passwords are stored hashed. Sessions are stated as outcomes (expiry, ending on log out); the mechanism is not prescribed. The confirmed assumption that sessions use cookies is therefore not made a requirement, because the web pages and API run on separate web addresses where cookies are not sent between them.

### US-001: Sign up with email and password

**Priority:** critical

> As a visitor, I want to create an account with my email address and a password, so that I can post ideas and vote.

| ID | Given | When | Then |
|---|---|---|---|
| AC-001 | I am a visitor who is not logged in | I submit the sign-up form with a valid, unused email address and a password | an account is created and I am logged in |
| AC-002 | an account already exists for an email address | I try to sign up with the same email address (ignoring letter case) | no second account is created and I see a message that the email is already registered |
| AC-003 | I am on the sign-up form | I submit an invalid email format or an empty password | no account is created and I see a message that says which field needs correcting |
| AC-004 | I am on the sign-up form | I sign up with an email at any domain | the sign-up is accepted, because no company-domain restriction applies |
| AC-005 | I have signed up | I look for an email verification step | none is required before I can use the app |

### US-002: Passwords are stored securely

**Priority:** high

> As a user, I want my password to be stored in a protected form, so that it cannot be read back if the database is exposed.

| ID | Given | When | Then |
|---|---|---|---|
| AC-006 | an account has been created | the stored account record is inspected | the password appears only as a salted hash, never as plain text |
| AC-007 | the app is operating | any page, message or log output is reviewed | no password is displayed or written in readable form |

### US-003: Log in

**Priority:** critical

> As a registered user, I want to log in with my email and password, so that I can post ideas and vote.

| ID | Given | When | Then |
|---|---|---|---|
| AC-008 | I have an account | I submit my correct email and password | I am logged in and the interface shows that I am logged in |
| AC-009 | I am on the log-in form | I submit a wrong password or an unknown email | I stay logged out and see a generic message that does not reveal which of the two was wrong |
| AC-010 | I am logged in | I close the browser and come back after the session lifetime has passed | I am logged out and asked to log in again before posting or voting |
| AC-011 | I forgot my password | I look for a reset option | none is offered, as password reset is out of scope for this version |

### US-004: Log out

**Priority:** high

> As a logged-in user, I want to log out, so that nobody else using my device can act as me.

| ID | Given | When | Then |
|---|---|---|---|
| AC-012 | I am logged in | I choose log out | my session ends and I see the board as a visitor |
| AC-013 | I have logged out | I use the browser's back button or try to post or vote | the action is refused and I am prompted to log in |

## EPIC-002: Public ideas board

Anyone, logged in or not, can view all ideas ranked by vote count, highest first. Ties are ordered newest first (assumption). Every idea shows its vote count. Ideas cannot be edited or deleted, and there are no comments or categories in this version.

### US-005: View ideas ranked by votes without logging in

**Priority:** critical

> As a visitor, I want to see all ideas listed with the highest vote count first, so that I can see what the team cares about most without needing an account.

| ID | Given | When | Then |
|---|---|---|---|
| AC-014 | ideas with different vote counts exist | I open the board without logging in | all ideas are listed in descending order of vote count |
| AC-015 | a vote is added to an idea | I reload the board | the idea appears in the position matching its new count |
| AC-016 | no ideas exist | I open the board | I see a clear empty-state message inviting people to post the first idea |

### US-006: Order tied ideas newest first

**Priority:** medium

> As a visitor, I want ideas with equal votes to be ordered with the newest first, so that the order is predictable and new ideas get visibility.

| ID | Given | When | Then |
|---|---|---|---|
| AC-017 | two or more ideas have the same vote count | the board is shown | those ideas are ordered by posting time, newest first |
| AC-018 | an older idea and a newer idea tie, then the newer one gains a vote | the board is reloaded | the newer idea is listed above the older one |

### US-007: See the vote count on every idea

**Priority:** high

> As a visitor or user, I want each idea to show its title, short description and vote count, so that I can judge it at a glance.

| ID | Given | When | Then |
|---|---|---|---|
| AC-019 | an idea exists | it appears on the board | its title, short description and current vote count are visible, including zero for an idea with no votes |
| AC-020 | I am viewing the board | I look at any idea | no edit, delete, comment or category controls are present |

## EPIC-003: Posting ideas

Logged-in users post an idea consisting of a title and a short description. Visitors who try to post are prompted to log in. Editing and deleting posted ideas is out of scope (assumption).

### US-008: Post an idea

**Priority:** critical

> As a logged-in user, I want to post an idea with a title and short description, so that my colleagues can vote on it.

| ID | Given | When | Then |
|---|---|---|---|
| AC-021 | I am logged in | I submit the idea form with a title and a short description | the idea is saved with zero votes and appears on the board |
| AC-022 | I am logged in | I submit the form with an empty title or empty description | nothing is saved and I see which field is missing |
| AC-023 | I am logged in | I submit a title or description longer than the stated limit shown on the form | nothing is saved and I see a message about the limit |
| AC-024 | I have posted an idea | I look for a way to edit or delete it | none is offered, as this is out of scope for this version |

### US-009: Prompt visitors to log in when posting

**Priority:** high

> As a visitor, I want to be told I need to log in when I try to post, so that I know how to proceed.

| ID | Given | When | Then |
|---|---|---|---|
| AC-025 | I am not logged in | I try to open the post-idea form or submit an idea | no idea is created and I am prompted to log in or sign up |
| AC-026 | I was prompted and then log in | login succeeds | I am taken back to the board or the post form, not left on an error page |

## EPIC-004: Upvoting

Logged-in users upvote ideas. Each user has one vote per idea. Votes are permanent upvotes: no un-voting and no downvotes. Users may vote on their own ideas. Voting requires login (all assumptions confirmed as open).

### US-010: Upvote an idea

**Priority:** critical

> As a logged-in user, I want to upvote an idea, so that the ideas I support rank higher.

| ID | Given | When | Then |
|---|---|---|---|
| AC-027 | I am logged in and have not voted on an idea | I upvote it | its vote count increases by exactly one and the board order updates accordingly |
| AC-028 | I am logged in | I upvote an idea I posted myself | the vote is accepted and counted |
| AC-029 | I have upvoted an idea | I look for a way to remove my vote or downvote | none is offered, as votes are permanent upvotes |

### US-011: Limit to one vote per user per idea

**Priority:** critical

> As a team member, I want each user limited to one vote per idea, so that the ranking is fair.

| ID | Given | When | Then |
|---|---|---|---|
| AC-030 | I have already voted on an idea | I view the board | that idea shows that I have voted and its vote control is disabled or replaced |
| AC-031 | I have already voted on an idea | a second vote for the same idea is submitted, for example by double-click, a repeated request or a second browser tab | the count does not change and no duplicate vote is stored |
| AC-032 | I have voted on one idea | I vote on a different idea | that vote is accepted |

### US-012: Prompt visitors to log in when voting

**Priority:** high

> As a visitor, I want to be told I need to log in when I try to vote, so that I know how to take part.

| ID | Given | When | Then |
|---|---|---|---|
| AC-033 | I am not logged in | I try to upvote an idea | no vote is recorded, the count is unchanged, and I am prompted to log in or sign up |
| AC-034 | I am not logged in | I view the board | vote counts are visible and vote controls are still shown, leading to the log-in prompt |

## EPIC-005: Responsive layout

The app is a responsive web app for desktop and mobile browsers. No native app.

### US-013: Use the board on desktop and mobile browsers

**Priority:** high

> As a team member, I want the board and forms to work on both a phone and a desktop browser, so that I can vote and post from any device.

| ID | Given | When | Then |
|---|---|---|---|
| AC-035 | I use a phone-sized screen (around 360 pixels wide) | I view the board and the sign-up, log-in and post forms | content fits without horizontal scrolling and controls can be tapped comfortably |
| AC-036 | I use a desktop-sized screen | I view the board | the layout uses the space sensibly and remains readable |
| AC-037 | I use a current version of a major desktop or mobile browser | I complete sign up, log in, post and vote | every step works |

## EPIC-006: Stored data

Accounts, ideas and votes are kept in a simple relational database (SQLite or Postgres) behind a standard full-stack web framework. No external services or API keys are needed, there are no payments, and no specific regulation applies (general industry). Only the email address is kept as personal data. Expected load is low: a few dozen trusted colleagues.

### US-014: Keep accounts, ideas and votes

**Priority:** critical

> As a team member, I want accounts, ideas and votes to be saved, so that nothing is lost when the app is restarted.

| ID | Given | When | Then |
|---|---|---|---|
| AC-038 | accounts, ideas and votes exist | the app is restarted | all of them are still present and the board shows the same ranking |
| AC-039 | the data is stored | the vote records are examined | a user and an idea can appear together in at most one vote |
| AC-040 | the app runs | its features are used | no external service, payment provider or API key is required |

### US-015: Keep personal data minimal

**Priority:** medium

> As a team member, I want only my email address kept as personal data, so that little about me is stored.

| ID | Given | When | Then |
|---|---|---|---|
| AC-041 | I sign up | I review the sign-up form and stored account record | only my email address and my hashed password are collected, with no other personal details |
| AC-042 | I view the board as a visitor or another user | ideas are shown | other users' email addresses are not displayed unless the team later decides otherwise |

## EPIC-007: Setup and usage documentation

Basic documentation so the team can run and use the board. Any credential shown must be a placeholder in angle brackets.

### US-016: Setup and usage guide

**Priority:** medium

> As a team member who runs the app, I want a short guide to set up, start and use the board, so that I can get it running and explain it to colleagues.

| ID | Given | When | Then |
|---|---|---|---|
| AC-043 | a person with the project files and a clean machine | they follow the setup guide | the app starts and the board is reachable, without needing any external service |
| AC-044 | the guide is read | a new colleague looks for usage help | it explains how to sign up, log in, post an idea, upvote, and states the limits (no editing, deleting, un-voting, password reset or email verification) |
| AC-045 | the guide mentions configuration values such as secrets | it is reviewed | they appear only as placeholders in angle brackets, never as real-looking values |
<!-- sdlc:auto:end epics -->
