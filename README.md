# Reddit → Amplitude Event Pipeline

**Growth Engineering Take-Home**
**Author:** Taranveer Flora

---

## 1. Executive Summary

This project is a minimal, reliable event ingestion and analytics pipeline.

The system will:

- Poll Reddit on a schedule
- Identify new posts
- Deduplicate them safely
- Send structured events to Amplitude
- Serve a simple web UI showing current front-page posts

The focus of this project is not UI polish or infrastructure complexity. The focus is reliability, correctness, and growth-oriented event design.

This is intentionally built as a small but production-minded system.

---

## 2. Problem Framing

This project simulates a real-world growth engineering workflow.

Instead of tracking user behavior in a product, we are:

- Tracking new Reddit posts
- Converting them into structured events
- Sending them into an analytics system

The real evaluation here is:

> Can I build a reliable ingestion and tracking system that does not double-count events and does not miss events?

In growth systems, corrupted data leads to bad decisions. This project models that reality.

---

## 3. System Requirements

### Functional Requirements

- Fetch posts from /r/healthcare
- Detect newly appearing posts
- Send exactly one analytics event per post
- Persist post IDs across runs
- Display current front-page posts in a web interface

### Non-Functional Requirements

- No duplicate events
- No race conditions
- Persistent state across executions
- Automatically scalable
- Clean separation of responsibilities
- Concise implementation

---

## 4. Architectural Philosophy

This project is designed around three principles:

**1. Reliability Over Flash**

The correctness of event tracking is more important than frontend polish.

**2. Infrastructure Abstraction**

The goal is to focus on backend logic and system design, not DevOps configuration.

**3. Growth-Oriented Thinking**

Every post represents a product event. The system is designed the same way a real analytics pipeline would be built in production.

---

## 5. Why Modal

Modal allows Python functions to run in the cloud without manual infrastructure setup.

Instead of configuring servers, containers, cron jobs, and scaling logic manually, Modal provides:

- Scheduled execution
- ASGI web serving
- Persistent storage
- Automatic scaling

This eliminates infrastructure noise and allows engineering focus to remain on:

- Data ingestion
- Deduplication
- Event correctness
- System clarity

For a growth engineer role, this is ideal. The evaluation should measure engineering judgment and reliability, not AWS configuration skills.

It also reflects modern startup infrastructure patterns, particularly in AI-native companies.

---

## 6. Why Amplitude

Amplitude is a product analytics platform used to track structured events inside products.

In a real company, events might include:

- `user_signed_up`
- `onboarding_completed`
- `subscription_started`
- `referral_sent`

In this project, each new Reddit post represents an event.

Sending structured, clean, non-duplicated events into Amplitude mirrors real growth engineering responsibilities:

- Ensure accurate tracking
- Maintain event integrity
- Prevent data corruption
- Support downstream analysis

The key signal here is understanding that analytics reliability is critical. Duplicate events distort metrics. Missing events corrupt insights.

This system is built to avoid both.

---

## 7. High-Level System Architecture

The system consists of five components:

1. Reddit as the external data source
2. A scheduled poller
3. Persistent storage for deduplication
4. An event sender
5. A web UI

**Flow:**

1. The poller retrieves Reddit front-page data.
2. It checks stored post IDs to determine which posts are new.
3. For each new post:
   - Emit a structured analytics event.
   - Record the post ID to prevent future duplication.
4. The current front-page state is stored.
5. The web UI reads from storage and displays the posts.

Each component has a single responsibility.

---

## 8. Deduplication Strategy

Deduplication is the core engineering challenge.

The poller runs on an interval. Posts may persist across multiple polling cycles.

Without careful design, the same post would generate multiple events.

Additionally, if multiple poller instances execute concurrently, a race condition could cause duplicate events.

The system must guarantee:

- Each post produces exactly one analytics event.
- The deduplication mechanism is safe under concurrent execution.
- State persists between runs.

This requires atomic check-and-store behavior at the storage layer.

This is the most critical part of the system.

---

## 9. Persistence Strategy

The system requires two categories of persistent state:

1. A set of previously seen post IDs
2. The current front-page posts

Persistence must survive:

- Function restarts
- Container scaling
- Scheduled execution intervals

State must also be shared across executions.

This ensures consistency and reliability.

---

## 10. Web Interface Scope

The web UI is intentionally minimal.

Its purpose is to:

- Display current front-page posts
- Confirm ingestion is functioning
- Provide basic visibility into system state

It is not intended to be a frontend-heavy product.

The evaluation focus is backend engineering quality.

---

## 11. Scalability Considerations

The system is designed to scale without re-architecture.

- Scheduled jobs can scale horizontally.
- The web server can scale under load.
- Persistent storage remains centralized.

This aligns with growth engineering priorities:

> Build systems that can handle increasing volume without rewrites.

---

## 12. What This Demonstrates

This project demonstrates:

- Understanding of serverless architecture
- Event-driven system design
- Growth analytics pipeline thinking
- Race-condition awareness
- Deduplication strategy design
- Pragmatic scope control
- Infrastructure abstraction judgment

It shows an ability to think beyond "make it work" and toward "make it reliable."

---

## 13. Tradeoffs & Scope Control

Intentionally excluded:

- Complex frontend
- Retry queues
- Advanced monitoring
- Distributed locking layers
- Over-engineering

The goal is clarity and correctness within time constraints.

---

## 14. Future Extensions

If productionizing:

- Add structured logging
- Add event retry handling with idempotency safeguards
- Add monitoring for failed analytics sends
- Add rate limit backoff handling
- Add unit and concurrency tests
- Add event schema versioning

---

## 15. Summary

This system models a real growth event ingestion pipeline:

> External signal → Ingestion → Deduplication → Analytics → UI

The focus is correctness and reliability over complexity.

The design prioritizes:

- Clean architecture
- Safe event tracking
- Scalability
- Minimal infrastructure overhead

The core challenge is not fetching Reddit posts.

The core challenge is guaranteeing accurate, race-free event emission.

That is what this system is built to solve.
