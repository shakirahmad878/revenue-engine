# Global Agent Instructions & Isolation Guidelines

## 🔒 1. Strict Conversation & Project Isolation Rule
* **Independent Context:** Every new conversation must be treated as a **completely new, independent project/task**, even if opened in the same workspace folder or repository.
* **No Cross-Conversation Pollution:** Never assume, carry over, mix, or modify past projects, background servers, or code from previous conversations unless the user explicitly references or asks for it.
* **Preserve Dedicated Ports & Background Services:** Dedicated background services (such as Port 8000 for the Autonomous Revenue Engine) must remain running and isolated. Never terminate, overwrite, or mount other projects onto active dedicated servers.

---

## ⚡ 2. Scope & Execution Rules
* Work strictly within the scope requested by the user in the current conversation turn.
* If a new project is introduced in this folder, house it in its own distinct sub-directory or isolate its dependencies and server ports completely.
