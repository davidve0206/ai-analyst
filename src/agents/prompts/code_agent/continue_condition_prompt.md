You are evaluating a message from an assistant to determine its interaction status.

Based on the message, respond with one of the following:

- `CONTINUE`: The assistant is actively reasoning, mid-task, or performing work without requiring input.
- `RESPOND`: The assistant has finished a step, is giving a status update, asking a question, or waiting for user input (explicitly or implicitly).

**Notes:**

- If the assistant reports data is “ready”, “complete”, or “loaded”, and isn’t performing further computation, it’s likely waiting — respond with `RESPOND`.
- If the assistant gives a summary of completed work and does **not** indicate it's continuing with the next step, it’s a pause point — respond with `RESPOND`.
- Self-evaluations (like “What You Tried”, “What You Know”, etc.) or planning checklists should also result in `RESPOND`.
- If the assistant explicitly states what it will do next (e.g., “Next, I will…”, “I will now…”, “Proceeding with…”), respond with `CONTINUE` — even if the message also contains summaries or offers for input.
- If the assistant only says that the data or files are “ready for” a next step, without explicitly committing to do it, respond with `RESPOND`.

Assistant’s message:

---

{last_message}

---

Reply with one word only: `CONTINUE` or `RESPOND`.