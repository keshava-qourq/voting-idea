<!-- sdlc:auto:start adr -->
# ADR-0001: Use React 19 for Frontend

Status: Accepted  
Date: 2026-11-25

## Context and Problem Statement

Which Frontend technology does the project use? Decided in architecture v1.

## Considered Options

- React 19

## Decision Outcome

Chosen option: React 19, because Approved by the product owner. It handles the re-ordering board, the forms and the responsive layout, and keeps the session token in client state to send as a Bearer header.

## Consequences

A static SPA means the token lives in browser storage, not an HttpOnly cookie. This is required by the two-origin deployment and mitigated by short session lifetime and server-side revocation.
<!-- sdlc:auto:end adr -->