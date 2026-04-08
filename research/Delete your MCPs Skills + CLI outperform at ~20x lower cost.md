---
title: "Delete your MCPs: Skills + CLI outperform at ~20x lower cost"
source: "https://agentnativedev.medium.com/i-deleted-all-my-mcps-skills-cli-outperform-at-20x-lower-cost-8e86e05fcca6"
published: 2026-03-12
created: 2026-04-06
description: "MCP servers inject 10,000–55,000 tokens of tool schemas but CLI tools cost 200–500 tokens for the same capability."
tags:
  - "clippings"
author:
  - "Agent Native"
---
[Sitemap](https://agentnativedev.medium.com/sitemap/sitemap.xml)

GitHub’s official **Copilot MCP server exposes 43 tools**.

Connecting it injects roughly **55,000 tokens** into your context window before your agent reads a single line of code.

The model **starts paying before it starts thinking**.

At Claude Sonnet 4 pricing ($3/M input tokens), that’s $0.16 per session just for tool definitions. Run 10,000 automated sessions per day and you’re burning **$1,600 daily** on plumbing.

**CLI tools cost 200–500 tokens for the same capability, and skills add progressive disclosure on top: 30–50 tokens at rest**, full instructions only when triggered.

Moreover, **CLI is 10–32x cheaper than MCP with 100% reliability, and Skills improve agent pass rates.**

This is really about **physics** more than anything.

This guide is a technical examination of **why Skills + CLI architectures produce better agent outputs than MCP-heavy setups**, grounded in token economics, attention research, and real benchmarks.

I’ll walk you through the **evidence**, show you the **code**, and let you decide.

If you’re building agents in production, this will **save you money**. If you’re evaluating agentic coding tools, this will **sharpen your framework**. If you’re designing agent architectures, this might **change how you think about tool interfaces entirely**.

## The gh --help vs MCP Spec Comparison

Here’s what the same capability looks like in practice:

```c
# CLI approach: ~200 tokens
$ gh issue create --help
Create an issue on GitHub.
  
Usage:
gh issue create [flags]
  
Flags:
-a, --assignee login Assign people by their login
-b, --body string  Supply a body
-l, --label name Add labels by name
-t, --title string Supply a title
...
```

The agent already knows `gh` from training data.

It composes the command in one shot.

Total interaction cost: under 500 tokens.

Compare that to the MCP equivalent: the server typically sends a full JSON schema for `create_issue` plus 42 other tools the agent will never touch.

> **Agentic SaaS** patterns are powering the most innovative products of 2026.
> 
> **You can read it here:** [***A* gentic SaaS Patterns Winning in 2026**](https://www.agentnative.dev/agentic-saas)*,* packed with real-world examples, architectures, and workflows you won’t find anywhere else.

## The MCP Tax Is Real

[Scalekit recently ran 75 benchmarks](https://www.scalekit.com/blog/mcp-vs-cli-use) comparing CLI, CLI+Skills, and MCP against identical tasks on the same model (Claude Sonnet 4).

The numbers:

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*_O9_e5wC4ItoHTr2efwzOA.png)

That’s a **32x token difference** for the simplest task, “what language is this repo?”

The MCP agent carried schemas for webhook management, gist creation, and PR review configuration.

It used one tool.

And it failed 28% of the time.

Every failure was a TCP timeout to GitHub’s remote MCP server.

CLI runs locally. There’s nothing to time out.

## Why This Isn’t Just About Money

Anthropic’s own engineering team also documented how direct MCP tool calls force intermediate results through the model’s context:

> *“Every intermediate result must pass through the model. In this example, the full call transcript flows through twice. For a 2-hour sales meeting, that could mean processing an additional 50,000 tokens.”*

They demonstrated a reduction from **150,000 tokens to 2,000 tokens,** a 98.7% saving, by switching from direct MCP tool calls to a code execution approach where the agent discovers tools on-demand through a file system.

The token cost is also cognitive.

Every token you waste on schema definitions is a token your agent can’t use for reasoning.

## Context Degradation: Models Get Dumber As Context Fills Up

Chroma Research’s “Context Rot” study tested 18 state-of-the-art models and found:

- **Performance degrades consistently with increasing input length,** across all models, even for simple tasks
- When needle-question similarity decreases (more realistic scenarios), **degradation accelerates**
- Models performed better on **randomly shuffled text** than logically ordered content, a structural paradox that shows attention mechanisms don’t behave as you’d expect
- **Claude abstains when uncertain; GPT confidently hallucinates** — different failure modes, same root cause
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*wLxeS9IT1V2bEybhBaZzyw.png)

The Stanford “Lost in the Middle” paper has already established the foundational finding: performance follows a **U-shaped curve**.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Pzz9JiQ-ltuV_PP8QAqtCQ.png)

Models recall information at the beginning and end of context well, but accuracy can drop **over 30%** for information positioned in the middle.

Anthropic’s context engineering guide introduced a useful framing here:

> *“Like humans, who have limited working memory capacity, LLMs have an ‘attention budget’ that they draw on when parsing large volumes of context. Every new token introduced depletes this budget.”*

Transformers create n² pairwise relationships for n tokens. As context grows, the model’s ability to capture these relationships gets stretched thin.

Models develop attention patterns from training data where shorter sequences are more common, meaning they have fewer specialized parameters for long-range dependencies.

This is an architectural property.

Position encoding interpolation allows handling longer sequences, but with degradation in token position understanding.

The U-shaped attention curve, strong at beginning and end, weak in the middle, persists.

This means that Your MCP tool schemas land in the middle of the context. That’s the worst possible position for information the agent might need to reference.

## What This Means for Agents in Practice

Agents in long contexts get stuck in **loops**, repeating the same ineffective action until step limits were reached.

They forget constraints established earlier and they misrepresent states that were valid earlier but had changed.

Now connect this to MCP.

A typical MCP-heavy setup consumes 51% of context before a single message:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*VQGZ8WKHqFGebyqrkc96ag.png)

You’re starting every conversation at the 50-yard line and by the time you add code files, conversation history, and tool outputs, you’re deep in the degradation zone.

## The Quadratic Trap

Multi-turn agent loops make this worse.

Stevens Institute research also documented how token costs grow quadratically:

> *“A Reflexion loop that runs for 10 cycles can consume 50x the tokens of a single linear pass. Research indicates that an unconstrained agent can cost $5 to $8 per task.”*

Each turn carries the full history.

With MCP schemas baked into every turn, you’re compounding waste.

## The Skills Architecture: Progressive Disclosure for Agents

Skills are a three-tiered progressive disclosure system.

The pattern was formalized in Anthropic’s Agent Skills specification and has since been adopted by Claude Code, OpenAI Codex, Cursor, and Gemini CLI.

The core idea: **don’t tell the agent everything upfront. Give it a table of contents and let it load what it needs.**

```c
# Three-Layer Architecture
Layer 1: Metadata (always loaded)
→ Skill name + one-line description
→ Cost: ~10-30 tokens per skill
→ Agent knows WHAT exists
  
Layer 2: Full SKILL.md (loaded on demand)
→ Complete instructions, workflows, constraints
→ Cost: ~200-2,000 tokens per skill
→ Agent knows HOW to do it
  
Layer 3: Reference docs (loaded when needed)
→ API specs, deep-dive documentation
→ Cost: ~2,000-20,000 tokens per skill
→ Agent handles EDGE CASES
```

With a 200k context window, loading all skills upfront eats ~10% immediately. Skills typically use <1%.

## How Skills Differ From Tools

There is a fundamental difference:

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*t9rUdSNntA9YKx6oCLQdnQ.png)

Skills don’t replace tools but they **teach the agent when and how to use tools**.

A Jira MCP server exposes functions but Jira Skill says: “I’m in finance, my project space is FIN-, create tickets with High priority by default.”

## Why 2–3 Skills Is the Sweet Spot

[SkillsBench](https://arxiv.org/html/2602.12670v1), the first rigorous benchmark for skill augmentation, tested 7,308 trajectories across Claude Code, Gemini CLI, and Codex CLI. One finding that jumped out:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*oYWfb_pjcTpJPPo2QvmNNQ.png)

More skills doesn’t mean better performance and the optimal design is **2–3 focused skills per task**.

Skill complexity matters too. **Detailed** skills (+18.8pp) outperformed **Comprehensive** ones (-2.9pp).

## CLI-First Agent Design: Code Examples and Patterns

**Pattern 1: CLI Composition Over MCP Orchestration**

When a skill wraps a CLI tool, the agent can **compose,** chaining Unix pipes the way it learned from millions of training examples:

```c
# Agent-composed CLI pipeline: find failed deployments
aws cloudwatch get-metric-data \
--metric-name FailedDeployments \
--start-time 2026-03-11T00:00:00Z \
--end-time 2026-03-12T00:00:00Z \
--output json | \
jq '.MetricDataResults[] | select(.Values[] > 0)' | \
sort -k2 -rn | head -20
```

When a Skill wraps an MCP tool, it must be **prescriptive**.

The agent can’t improvise MCP tool chains because there’s no composability grammar in its training data.

Every operation becomes a sequential round-trip.

**Pattern 2: The 800-Token Skill File**

800-token skill file, just a document of `gh` tips, can reduce tool calls by a third and latency by a third versus naive CLI:

```c
# github-skill.md (~800 tokens)
## Repository Operations
- Use \`gh repo view --json name,description,primaryLanguage\` for structured output
- Use \`gh api repos/{owner}/{repo}\` for fields not in the CLI
- Pipe to \`jq\` for filtering: \`gh pr list --json number,title | jq '.[] | select(.title | test("fix"))'\`
  
## PR Workflows
- \`gh pr list --state merged --limit 20 --json number,title,mergedAt\`
- \`gh pr view {number} --json files,additions,deletions\` for diff stats
- Chain: \`gh pr list --json number | jq '.[].number' | xargs -I{} gh pr view {} --json title,body\`
  
## Issue Patterns
- \`gh issue list --label bug --state open --json number,title,labels\`
- Create with files: \`gh issue create --title "Bug" --body-file ./description.md\`
  
## Output Tips
- Always use \`--json\` flag for structured data
- Use \`jq\` for filtering, not grep on formatted output
- \`gh api\` supports GraphQL: \`gh api graphql -f query='{ repository(owner:"org", name:"repo") { ... } }'\`
```

The agent already knows `gh` and te skill just sharpens its instincts.

**Pattern 3: Code Execution Over Tool Calls**

[Anthropic’s code execution pattern](https://www.anthropic.com/engineering/code-execution-with-mcp) moves data processing out of the context window entirely:

```c
// Instead of MCP tool calls flowing 10k rows through context:
// TOOL CALL: gdrive.getSheet(sheetId: 'abc123') → 10,000 rows in context
  
// Code execution: filter happens outside the context window
import * as gdrive from './servers/google-drive';
  
const allRows = await gdrive.getSheet({ sheetId: 'abc123' });
const pendingOrders = allRows.filter(row =>
row["Status"] === 'pending'
);
console.log(\`Found ${pendingOrders.length} pending orders\`);
console.log(pendingOrders.slice(0, 5)); // Only 5 rows enter context
```

The agent writes code that calls tools rather than calling tools directly. Data never touches the context window unless the agent explicitly logs it.

**Pattern 4: File System as Context Store**

```c
// Persist state between execution steps without context overhead
const leads = await salesforce.query({
query: 'SELECT Id, Email FROM Lead LIMIT 1000'
});
const csvData = leads.map(l => \`${l.Id},${l.Email}\`).join('\n');
await fs.writeFile('./workspace/leads.csv', csvData);
  
// Later execution picks up where it left off - zero context cost
const saved = await fs.readFile('./workspace/leads.csv', 'utf-8');
```

This pattern keeps the context window clean. The file system becomes the agent’s long-term memory.

## The Decision Framework

Here’s when CLI + Skills wins:

- **Developer tools** where the agent acts as the user
- **Agentic coding** workflows (debugging, refactoring, deployment)
- **Local data processing** with high-frequency loops
- **Mature vendor CLIs** (AWS, GitHub, GCP, kubectl)
- **Token-sensitive production** at scale (10k+ sessions/day)

When MCP still makes sense:

- **Multi-tenant SaaS** where agents act on behalf of customers
- **Enterprise auth** requiring per-user OAuth, RBAC, and audit trails
- **Services with no CLI** (most SaaS APIs)
- **Compliance requirements** needing structured, queryable records of every agent action

You can also adopt the hybrid architecture as the production answer isn’t CLI **or** MCP.

It’s Skills on top of both:

```c
┌─────────────────────────────────┐
│ Skills Layer                    │  ← 30-50 tokens at rest
│  (What to do + domain context)  │  ← Progressive disclosure
├─────────────────────────────────┤
│ CLI Transport       │ MCP       │
│  (local tools, gh,  │ (OAuth,   │  ← Execution layer
│ aws, kubectl)       │  SaaS)    |
├─────────────────────────────────┤
│  File System / State            │  ← Persistence outside context
└─────────────────────────────────┘
```

Skills sit on top as the intelligence layer.

They route to CLI for local work and MCP for governed external access.

The agent doesn’t know or care which transport handles the execution.

## Bonus Articles

## [7 Local LLM Families To Replace Claude/Codex (for everyday tasks)](https://agentnativedev.medium.com/7-local-llm-families-to-replace-claude-codex-for-everyday-tasks-25ba74c3635d?source=post_page-----8e86e05fcca6---------------------------------------)

### Open-source model families you can run locally that are now delivering real-world performance surprisingly close to…

agentnativedev.medium.com

## [I Ignored 30+ OpenClaw Alternatives Until OpenFang](https://agentnativedev.medium.com/i-ignored-30-openclaw-alternatives-until-openfang-ff11851b83f1?source=post_page-----8e86e05fcca6---------------------------------------)

### Fully open-source Agent Operating System, written entirely in Rust, shipping as a single 32 MB binary with a 180 ms…

agentnativedev.medium.com

## [Deep Agents: The Harness Behind Claude Code, Codex, Manus, and OpenClaw](https://agentnativedev.medium.com/deep-agents-the-harness-behind-claude-code-codex-manus-and-openclaw-bdd94688dfdb?source=post_page-----8e86e05fcca6---------------------------------------)

### The biggest lessons and hard-won best practices for building agent harnesses from Anthropic, OpenAI and LangChain

agentnativedev.medium.com

## [Qwen 3.5 35B-A3B: Why Your $800 GPU Just Became a Frontier Class AI Workstation](https://agentnativedev.medium.com/qwen-3-5-35b-a3b-why-your-800-gpu-just-became-a-frontier-class-ai-workstation-63cc4d4ebac1?source=post_page-----8e86e05fcca6---------------------------------------)

### I have been running local models for a while now, and I thought I had a pretty good sense of where the ceiling was for…

agentnativedev.medium.com

## [GET SH\*T DONE: Meta-prompting and Spec-driven Development for Claude Code and Codex](https://agentnativedev.medium.com/get-sh-t-done-meta-prompting-and-spec-driven-development-for-claude-code-and-codex-d1cde082e103?source=post_page-----8e86e05fcca6---------------------------------------)

### GSD (“Get Shit Done”) aims to solve context rot, the quality degradation as the model’s context window fills.

agentnativedev.medium.com

## [OpenClaw Memory Systems That Don’t Forget: QMD, Mem0, Cognee, Obsidian](https://agentnativedev.medium.com/openclaw-memory-systems-that-dont-forget-qmd-mem0-cognee-obsidian-4ad96c02c9cc?source=post_page-----8e86e05fcca6---------------------------------------)

### If your agent has ever randomly ignored a decision you know you told it… it’s not random.

agentnativedev.medium.com

## [Fully Autonomous Companies: OpenClaw Gateway + Routing + Agents](https://agentnativedev.medium.com/fully-autonomous-companies-openclaw-gateway-routing-agents-412d67df5138?source=post_page-----8e86e05fcca6---------------------------------------)

### Whether you think it’s hype or not, people are already trying to run fully autonomous companies on OpenClaw.

agentnativedev.medium.com

[![Agent Native](https://miro.medium.com/v2/resize:fill:96:96/1*dt5tcaKMBhB6JboQ9lIEAA.jpeg)](https://agentnativedev.medium.com/?source=post_page---post_author_info--8e86e05fcca6---------------------------------------)

[![Agent Native](https://miro.medium.com/v2/resize:fill:128:128/1*dt5tcaKMBhB6JboQ9lIEAA.jpeg)](https://agentnativedev.medium.com/?source=post_page---post_author_info--8e86e05fcca6---------------------------------------)

[0 following](https://agentnativedev.medium.com/following?source=post_page---post_author_info--8e86e05fcca6---------------------------------------)

Hyperscalers, open-source developments, startup activity and the emerging enterprise patterns shaping agentic AI.

## Responses (3)

Michael James Wilson

What are your thoughts?  

```c
In complete agreement with your assessment.This is one of the reason I started building Matimo (https://matimo.dev), currently it supports specific tools which are simple cli tools and api calls when agent requires they can call and execution is via…
```

2

```c
I think this is an indication of bad MCP tools, not that MCP tooling is inherently worse than CLI + skills.MCP is useful exactly when you need high-level capabilities that are useful for LLM tasks which _aren't_ trivially replicated with CLI tools…
```

1

```c
MCP (channels) also wins for asynchronous inbound notifications vs polling.
```

1