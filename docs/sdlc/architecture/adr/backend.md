<!-- sdlc:auto:start adr -->
# ADR-0002: Use FastAPI 0.115 for Backend

Status: Accepted  
Date: 2026-11-25

## Context and Problem Statement

Which Backend technology does the project use? Decided in architecture v1.

## Considered Options

- FastAPI 0.115

## Decision Outcome

Chosen option: FastAPI 0.115, because Approved by the product owner. A small API covers sign-up, log-in, log-out, list, post and vote, with Pydantic validation for email format and length limits. Sessions are server-side opaque tokens instead of cookies.

## Consequences

Auth is hand-built (hashing, session table) instead of coming from a full-stack framework, which is a small amount of code for this scope.
<!-- sdlc:auto:end adr -->