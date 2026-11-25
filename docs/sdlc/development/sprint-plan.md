# Sprint Plan

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start sprints -->
## Sprint 1: Sprint 1

Foundation: persistent schema, secure password storage, sign up, log in and log out

Capacity: 20 points · Committed: 19

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-001 | Story | Sign up with email and password | 5 | backend-agent | US-014, US-002 |
| US-002 | Story | Passwords are stored securely | 2 | backend-agent | US-014 |
| US-003 | Story | Log in | 5 | backend-agent | US-001, US-014 |
| US-004 | Story | Log out | 2 | backend-agent | US-003 |
| US-014 | Story | Keep accounts, ideas and votes | 5 | backend-agent | — |

## Sprint 2: Sprint 2

Core loop: public ranked board, posting ideas and upvoting

Capacity: 20 points · Committed: 19

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-005 | Story | View ideas ranked by votes without logging in | 5 | backend-agent | US-014 |
| US-006 | Story | Order tied ideas newest first | 1 | backend-agent | US-005 |
| US-007 | Story | See the vote count on every idea | 2 | frontend-agent | US-005 |
| US-008 | Story | Post an idea | 5 | backend-agent | US-003, US-005 |
| US-010 | Story | Upvote an idea | 5 | backend-agent | US-003, US-005, US-014 |
| US-015 | Story | Keep personal data minimal | 1 | backend-agent | US-001, US-005 |

## Sprint 3: Sprint 3

Visitor log-in prompts, one-vote UX, responsive layout and documentation

Capacity: 20 points · Committed: 15

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-009 | Story | Prompt visitors to log in when posting | 3 | frontend-agent | US-008, US-003 |
| US-011 | Story | Limit to one vote per user per idea | 3 | backend-agent | US-010 |
| US-012 | Story | Prompt visitors to log in when voting | 2 | frontend-agent | US-010, US-009 |
| US-013 | Story | Use the board on desktop and mobile browsers | 5 | frontend-agent | US-005, US-008, US-003 |
| US-016 | Story | Setup and usage guide | 2 | devops-agent | US-003, US-008, US-010 |

## Unscheduled

_Nothing unscheduled._
<!-- sdlc:auto:end sprints -->
