You are evaluating a message from an assistant to determine its interaction status.

Based on the message, respond with one of the following:

- `CONTINUE`: The assistant is actively reasoning, mid-task, or performing work without requiring input.
- `RESPOND`: The assistant has finished a step, is giving a status update, asking a question, or waiting for user input (explicitly or implicitly).

**Notes:**

- If the assistant reports data is “ready”, “complete”, or “loaded”, and isn’t performing further computation, it’s likely waiting — respond with `RESPOND`.
- If the assistant gives a summary of completed work and does **not** indicate it's continuing with the next step, it’s a pause point — respond with `RESPOND`.
- Self-evaluations (like “What You Tried”, “What You Know”, etc.) or planning checklists should also result in `RESPOND`.

Assistant’s message:

---

{last_message}

---

Reply with one word only: `CONTINUE` or `RESPOND`.
