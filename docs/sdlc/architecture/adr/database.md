<!-- sdlc:auto:start adr -->
# ADR-0003: Use PostgreSQL 16 for Database

Status: Accepted  
Date: 2026-11-25

## Context and Problem Statement

Which Database technology does the project use? Decided in architecture v1.

## Considered Options

- PostgreSQL 16

## Decision Outcome

Chosen option: PostgreSQL 16, because Approved by the product owner. Users, sessions, ideas and votes are plain tables. A UNIQUE (user_id, idea_id) constraint enforces one vote per user per idea even under concurrent requests.

## Consequences

A managed database instance costs a little more than a file database but gives durability across restarts and backups.
<!-- sdlc:auto:end adr -->