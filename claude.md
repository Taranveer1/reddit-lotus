Building a web application deployed on Modal that:

Polls r/healthcare via Reddit's public JSON API
Deduplicates posts by id and sends reddit_post_ingested events to Amplitude
Serves a FastAPI ASGI web UI showing current front page posts (title, link, author)

Stack: Python, Modal, FastAPI, Amplitude HTTP API v2, httpx
Style

NEVER use emojis unless explicitly requested
Be concise and direct
Explain rationale for architectural decisions
This is a 3-4 hour take-home -- every decision should optimize for shipping a working, clean, deployed app

Workflow (Follow This Order)

UNDERSTAND -> 2. PLAN -> 3. IMPLEMENT -> 4. VALIDATE

Before coding:

Read and understand the full requirement
Ask clarifying questions if ambiguous
Create detailed plan for non-trivial changes
Break large tasks into small, focused chunks
Get approval before starting significant work

After each change, verify:

 Single responsibility? (One job per function/class)
 Simplest solution? (No unnecessary complexity)
 No "just in case" code? (YAGNI)
 No duplicated knowledge? (DRY)
 Tests pass?
 Follows existing patterns?

Architecture Principles
SOLID (Always Apply)

Single Responsibility: One job per function/class/module
Open/Closed: Extend behavior, don't modify existing code
Liskov Substitution: Subtypes must be interchangeable
Interface Segregation: Small, specific interfaces
Dependency Inversion: Depend on abstractions, not concretions

Simplicity First (CRITICAL)

KISS: Always choose the simplest solution that works
YAGNI: Do NOT build features "just in case" -- wait for actual need
DRY: Single source of truth for every piece of knowledge
No premature optimization: Measure before optimizing
No premature abstraction: Don't create abstractions for single use
When unsure, prefer fewer files and less abstraction

Anti-Over-Engineering (ESPECIALLY IMPORTANT FOR THIS PROJECT)

Do NOT add configuration until you need configurability
Do NOT create abstract layers for one implementation
Do NOT add flexibility without actual use cases
Do NOT build event buffers, queues, state machines, or ops endpoints unless explicitly required
Do NOT build a separate dispatcher -- the poller can send to Amplitude directly after dedup
Start simple, add complexity ONLY when proven necessary
The assessment says "concise" -- respect that

Project-Specific Rules
What We ARE Building

A scheduled Modal function that polls Reddit and deduplicates by post id
An Amplitude event sender (called inline by the poller for new posts)
A FastAPI ASGI app that reads current posts from storage and renders HTML
Persistent storage for seen post IDs and current front page data

What We Are NOT Building

No React frontend -- server-rendered HTML is sufficient
No separate dispatcher or event buffer
No state machine (NEW/STORED/SENT) -- a simple seen_ids set is enough
No /internal/status or observability endpoints
No retry logic with backoff unless we have time at the end
No database -- Modal Dict or Volume is sufficient
No Docker, no CI/CD, no terraform

Deduplication (THE CORE CORRECTNESS REQUIREMENT)

Use a persistent set of seen post IDs
Check-and-write must be safe from races
Modal scheduled functions are single-concurrency by default -- leverage this
Document this decision explicitly in the README

Reddit API

Endpoint: https://www.reddit.com/r/healthcare.json
Set a custom User-Agent header (Reddit blocks default agents)
No auth required
Parse data.children[].data for post fields
Fields needed: id, title, author, permalink (construct full link from permalink)

Amplitude API

Use HTTP API v2: POST https://api2.amplitude.com/2/httpapi
Event type: reddit_post_ingested
Event properties: { title, link, author }
API key via environment variable (Modal secrets), never hardcoded

FastAPI Web UI

Single route: GET / returns HTML
Show each post's title (as clickable link), and author
Read current posts from the same persistent storage the poller writes to
Clean, readable HTML -- no framework needed, inline styles or minimal CSS is fine

Modal Deployment

Use @modal.function(schedule=modal.Period(minutes=5)) for the poller
Use @modal.asgi_app() for FastAPI
Use modal.Dict or modal.Volume for persistence
Secrets via modal.Secret.from_name()

Git Workflow -- STRICT RULES
NEVER Auto-Commit

NEVER commit without my explicit approval
NEVER push without my explicit approval

Before ANY Commit, Show Me:
Files to commit:
| Status | File            | Change Summary      |
|--------|-----------------|---------------------|
| M      | path/file.py    | Brief description   |
| A      | path/new.py     | Brief description   |

Commit message:
type(scope): description

Awaiting approval. Proceed? (yes/no)
Commit Message Format

Conventional commits: type(scope): description
Types: feat, fix, docs, style, refactor, test, chore
Subject < 72 chars, explain WHY not just WHAT

Code Quality
Structure

Functions: < 30 lines
Files: < 300 lines
Nesting: max 3 levels
Concepts per function: max 7 (Miller's Law)
Target: ~4-6 files total for this project

Naming

Self-documenting names
Booleans: is_, has_, can_, should_
Functions: verbs (fetch_posts, send_event, check_seen)
Keep naming consistent with the domain: posts, events, seen_ids

Security

Amplitude API key in Modal secrets, NEVER in code
Validate Reddit API response structure before processing
Custom User-Agent to respect Reddit's ToS

Error Handling

Handle Reddit API failures gracefully (log + skip cycle)
Handle Amplitude API failures gracefully (log, don't crash poller)
Never silently swallow exceptions
Meaningful error messages with context

What NOT To Do
Never

Add features not explicitly requested
Refactor code unrelated to current task
Add "improvements" beyond scope
Create files unless absolutely necessary
Over-engineer simple problems
Build abstractions for things used once

Avoid

Deep nesting (> 3 levels)
Long functions (> 30 lines)
Magic numbers/strings (use constants)
Premature optimization
Premature abstraction
Class hierarchies where functions suffice

Communication
When Stuck

Stop and explain the problem clearly
Propose 2-3 alternative approaches
Ask for guidance before proceeding

When Uncertain

Ask rather than assume
Present options with trade-offs
Get approval for architectural decisions