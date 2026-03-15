# System Architecture & Scaling Responses

This document answers essential architecture and scaling questions for the AI Journal System.

---

### Q1: How would you scale to 100k users?

To handle 100,000 active users effectively, we must move away from the current single-server, local-database architecture:

* **Separation and Load Balancing:** Deploy the backend API as a containerized microservice (using Docker and Kubernetes) across multiple nodes, placed behind a Load Balancer to distribute incoming traffic evenly.
* **Database Migration:** Replace the monolithic SQLite database with a robust, concurrent relational database like **PostgreSQL** or a NoSQL database tailored to documents like MongoDB. For a relational structure, implementing read-replicas will drastically improve query performance for dashboards.
* **Caching Layer:** Introduce an in-memory cache like **Redis** to store frequently accessed data (e.g., user profiles or recent dashboard statistics).
* **Asynchronous Processing:** Move the LLM request bottleneck into an asynchronous worker queue (via Celery/RabbitMQ or AWS SQS). Instead of the user waiting for the web request to resolve against the Gemini API, the backend should immediately return a `202 Accepted` status and process the AI analysis in the background, updating the UI via WebSockets or polling later.

---

### Q2: How would you reduce LLM cost?

Calling an LLM API repeatedly is the most expensive operational cost. We can mitigate this by:

* **Caching Repeated Results:** Cache the exact responses if users submit highly similar or identical text, skipping the LLM call entirely.
* **Batching Requests:** If performing background processing, batch multiple user analyses into a single prompt payload to the LLM when possible, reducing the volume of HTTP requests and token overhead.
* **Using Smaller/Cheaper Models:** Utilize faster, cheaper models (like Gemini 1.5 Flash or open-source alternatives like Llama-3 8B) for simple extraction tasks instead of large reasoning models (like GPT-4).
* **Limiting Request Size:** Truncate user text at the client or backend level before sending it to the LLM. Enforce strict character caps on journal entries so you never process massive token payloads.

---

### Q3: How would you cache repeated analysis?

Using a caching service like **Redis** is the absolute best approach:

1. When a user requests an analysis, calculate a fast, deterministic hash (like SHA-256) of the **normalized text** (lowercased, stripped of excess whitespace).
2. Look up this hash key in Redis.
3. **If a Cache Hit occurs:** Instantly return the pre-computed JSON response (emotion, keywords, summary) stored at that key.
4. **If a Cache Miss occurs:** Forward the text to the Gemini API. Once the result returns, save the mapping `[text_hash] -> [llm_result_json]` into Redis with an appropriate TTL (Time-To-Live). Then return the result to the user.

---

### Q4: How would you protect sensitive journal data?

Journal entries contain highly personal and sensitive emotional data, making security paramount:

* **Encryption at Rest:** Ensure the database filesystem encrypts all data at rest. Additionally, encrypt the actual `text` column values within the database using algorithms like AES-256, so a compromised database dump is unreadable without the decryption key.
* **Encryption in Transit:** Enforce strict HTTPS/TLS 1.2+ across the entire application stack. Never transmit plain-text journal data over HTTP.
* **Robust Authentication & Authorization:** Implement secure authentication (OAuth 2.0 or JWTs). Validate on backend endpoints that the authenticated user identity absolutely matches the `userId` attached to the requested journal records. Restrict cross-tenant data access.
* **Data Minimization & Anonymization (For AI APIs):** Strip Personally Identifiable Information (PII)—like names or addresses—from the journal texts *before* sending those texts over the network to a 3rd-party LLM provider like Gemini. Opt-out of data-sharing agreements where the LLM provider might use API submissions to train their commercial models.
