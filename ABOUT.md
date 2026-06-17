

## Why this role
I enjoy building AI-native products where the challenge is not just writing code, but deciding how to handle uncertainty, tradeoffs, and real-world constraints. This contact-finding challenge stood out because it focuses on planning, confidence scoring, provenance, and judgment rather than simply producing a working scraper.

## How you work with AI tools
I use AI tools such as ChatGPT, Claude, and Cursor as thinking partners rather than code generators. I typically use them to explore approaches, identify edge cases, review designs, and challenge assumptions. For implementation work, I verify outputs, modify generated code when needed, and prefer small testable iterations over blindly accepting model suggestions. I trust AI for speed and brainstorming, but I rely on reasoning, testing, and validation before adopting a solution.

## Your last project (structured — this is the pre-filter)
- **One ambiguity** you faced and how you resolved it:
In a WhatsApp AI Business Assistant project, the biggest ambiguity was deciding how much conversation history should be provided to the LLM. Too little context reduced response quality, while too much increased cost and latency. I resolved it by storing conversation history in a database and sending only the most relevant recent context to the model.
- **One tradeoff** you made and why:
I chose Supabase for persistence and authentication instead of building a custom backend data layer. This reduced development time and operational complexity, allowing me to focus on the AI workflow and user experience.
- **One mistake** you made and what you changed:
you made and what you changed:
Initially, I stored too much conversation history in prompts, which increased token usage and response times. After observing the impact, I redesigned the memory strategy to keep only relevant context and summarize older interactions.

- **One review comment** that made you change your mind:
A reviewer suggested separating business logic from API route handlers instead of placing everything inside FastAPI endpoints. After refactoring, the project became easier to test, maintain, and extend, and I adopted that pattern in later projects.
## Anything you'd improve about THIS challenge or our CLAUDE.md
I liked the emphasis on planning before implementation and on handling uncertainty honestly. One small improvement would be providing a sample expected output row in the problem statement so candidates can focus more time on reasoning and less time interpreting the output format. The challenge does a good job of rewarding judgment instead of rewarding the largest amount of code.
