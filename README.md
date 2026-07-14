# Policy Service Blueprinter

Turns **policy documents** — statutes, regulations, official agency guidance — into a visual service
blueprint: a government program's rules retold from the claimant's side, across who does what
(claimant / system / caseworker).

Requirements come from **policy only**. This skill does not map legacy system rules or requirements from other sources.

- **Colored Type tags** — level of legal authority (federal reg, state statute, state reg, agency guidance)
- **🛠** — agency operational practice, not strict law
- **⚖️** — a higher authority controls a lower one
- **⚠️** — a gap or ambiguity for a person to resolve

## Install

Copy this folder into your Claude skills directory:

- Personal: `~/.claude/skills/policy-service-blueprinter`
- One project: that project's `.claude/skills/policy-service-blueprinter`

Restart Claude to load.

## Use

1. Gather links to online policy sources or prepare markdown files of all policy documents.
2. In Claude Code or CoWork, paste your policy links or attach markdown files. Ask Claude to build a service blueprint from them.
3. Answer one scope question — the whole program, or one slice (e.g. just weekly certification, appeals, etc).
4. Open the HTML file thet Claude produces. Works on any browser, no setup.

## This is a draft

It AI-extracts legal requirements. Have a policy SME review every blueprint before it informs any
decision, system design, or public-facing communication.
