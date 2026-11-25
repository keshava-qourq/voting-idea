<!-- sdlc:auto:start adr -->
# ADR-0004: Use AWS for Cloud

Status: Accepted  
Date: 2026-11-25

## Context and Problem Statement

Which Cloud technology does the project use? Decided in architecture v1.

## Considered Options

- AWS

## Decision Outcome

Chosen option: AWS, because Approved by the product owner. S3 and CloudFront host the SPA, App Runner hosts the API on its own origin, and RDS hosts PostgreSQL. No other services are needed.

## Consequences

A single small instance of each keeps cost low but has no high availability, which is accepted for a few dozen colleagues.
<!-- sdlc:auto:end adr -->