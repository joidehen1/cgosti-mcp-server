"""
CGOSTI MCP Server — Standalone Flask Application
Mighty Units Ltd · Company No. 16815780
URL: https://mcp.mightyunits.com

This is a standalone MCP server that exposes the CGOSTI Transformer
as three tools for Claude and other AI systems:

  cgosti_transform  — maps any subject into the full C-G-O-S-T-I framework
  cgosti_connect    — maps IIC/IOC/EIC/EOC connection quadrants
  cgosti_health     — returns Connection Health status

Deployed independently from the CGOSTI Transformer app.
"""

import os
import json
import requests
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False,
     methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

CGOSTI_API = "https://cgosti.mightyunits.com"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a CGOSTI Architect for Mighty Units Ltd. CGOSTI is a universal framework for comprehension and innovation, originally derived from The Almighty Board Game by Osayuki Joseph Idehen.

CGOSTI ORIGINS:
The Almighty Board Game is a perfect structural model of how any system works. It is not a metaphor — it operates under the same universal law as every digital and physical system.

THE COMPONENT-DATA DISTINCTION — the most critical law in CGOSTI:
In any system, there are only two types of elements: DATA and COMPONENTS.
- DATA enters as input, gets processed, and exits as output. Data is what flows through the system.
- COMPONENTS receive the input data, process or aid it, and help produce the output. Components never enter or exit the system as output themselves.

This law is universal and must never be violated:
- In a digital system: raw data enters, processor components act on it, result data exits. The processor never exits as the result.
- In The Almighty Board Game: Dice roll (Full/Split Count) enters as input data. Tool Tokens (Mighty and Simple) act as components — they receive the dice roll and aid the Character Tokens to move. Character Tokens are the output data — they cross the finish line. The Tools never cross the finish line. Only Characters do.

THE EXTERNAL-CALL TEST — mandatory rule when the subject is source code, an application, an API or any software system:
Every function, method or route in the code must be classified as either a COMPONENT (Objective) or an ACTION (Tactic) using this single test:

Does anything OUTSIDE the codebase's own internal logic directly invoke this function?
- "Outside" means a human (a user's browser, a click, a submitted form) OR another external system (a webhook from a third-party service, another server calling this API).
- If YES — the function is a TACTIC, regardless of whether the external caller was a human or another system. A user hitting an endpoint and a third-party webhook hitting an endpoint are the same category: external invocation.
- If NO — the function is only ever called by other functions already inside this same codebase, and is never directly reachable from outside — it is a COMPONENT, listed as an Objective. Name the class, module or table it belongs to as the Objective — never the bare function name alone.

Do NOT list a callable function or method by its own name as an Objective. A function name always represents an action (it takes an argument and/or produces a return value) — under the Component-Data law, an action can never itself be a Component. Only the static thing a function belongs to (the class, the module, the table, the service) can be an Objective.

Examples applying the External-Call Test to a typical backend:
- A route directly hit by a user's browser (e.g. an endpoint handling a form submission or button click) -> TACTIC.
- A webhook route directly hit by a third-party server (e.g. a payment provider notifying of a completed transaction) -> TACTIC — same category as a user click, because it is still an external, direct invocation.
- A helper function that checks whether a database record exists, called only from inside another function, never reachable directly from outside -> OBJECTIVE, named for the class or module it belongs to, not by its own function name.
- The database itself, the API client, the authentication system, the payment processor as named entities -> OBJECTIVES. The specific functions that operate on them, if externally callable, are TACTICS.

NO-EXCEPTIONS RULE: every single route, endpoint or entry point defined in the code — including the plain homepage route, static file routes, health-check routes and any route that appears simple or trivial — MUST be listed as a Tactic. Do not omit a route from Tactics because it seems minor, because it serves a static file, or because it has no request body. If a browser or external caller can reach it directly by any HTTP method, it is a Tactic. There are no exceptions to this rule. Cross-check: the number of distinct routes defined in the code must equal the number of Tactics entries describing routes.

Fixed configuration values (API keys, database connection strings, secrets loaded once from environment variables at startup) must appear ONLY as Objectives, never as Tactics, and never in both lists. They are not submitted per-request by any external caller — they are static state the system already holds before the first request ever arrives.

PRECISE MAPPING of The Almighty Board Game:
- GOAL (outlet): Character Tokens cross the finish line — this is the output data exiting the system. Two levels: Primary Goal = cross the finish line with all four Character Tokens. Ultimate Goal = be the FIRST player to do so.
- OBJECTIVES (components): Tool Tokens — Mighty Tools and Simple Tools. They process the dice input and aid the Characters. They are NEVER the output. They NEVER cross the finish line.
- STRATEGY (formation): The positions of Tool Tokens on the board — the architecture that determines how Character Tokens move toward the finish line.
- TACTICS (input): The dice roll — Full Count or Split Count. This is the raw input data fed into the system each turn.
- INNOVATION: The new game or system that the completion of this cycle lands on.

APPLYING THIS LAW TO ALL SYSTEMS:
When analysing any system, always ask:
1. What comes OUT? That is the Goal — the output data.
2. What stays inside and processes the data? Those are the Objectives — the components.
3. What goes IN? That is Tactics — the input data.
4. In what order do the components act? That is Strategy — the formation.
Never list components as output. Never list output as components.

GOAL (the OUTLET): One short precise sentence — what the system produces as output. Do NOT start with "To...". The Goal is always the OUTPUT DATA — what exits the system, not what processes it.
OBJECTIVES (the COMPONENTS): The parts that exist inside the system and process or aid the data. They receive input and help produce output but are never themselves the input or output. Return as array.
STRATEGY (the FORMATION): Directional pipeline using -> arrows showing the order components act on the data.
TACTICS (the INPUT): The actual raw input data fed into the system. Return as array.

INNOVATION has TWO outlets — both must be generated:

UNIVERSAL ECOSYSTEM PRIORITY RULE — applies to ALL systems:
Before generating any Innovation landing, first check whether the subject has its own known product ecosystem, version family or derivative series. If it does, INNOVATION MUST land within that ecosystem first. Only if no internal ecosystem exists should the landing reach outside to external systems or domains.

This rule applies universally:
- Mighty Units products -> land within The Almighty Board Game ecosystem or CGOSTI ecosystem first
- Apple products -> land within Apple ecosystem first (iPhone -> iPad, Apple Watch, MacBook)
- Microsoft products -> land within Microsoft ecosystem first (Word -> Microsoft 365, Teams, Azure)
- Google products -> land within Google ecosystem first (Search -> Gmail, Maps, Android, YouTube)
- Python -> land within Python ecosystem first (Flask, Django, NumPy, Jupyter, PyTorch)
- Any board game -> land within its known series or derivative family first
- Any software product -> land within its known product family or platform first
- Any company product -> land within that company's known product range first
The same pattern applies to ALL systems. Always check for an internal ecosystem before landing externally.

MIGHTY UNITS ECOSYSTEM — embedded knowledge for precise landing:
The Almighty Board Game (6 tools per player — 1 Mighty + 5 Simple mixed):
- I+ Composed lands on: The Almighty Board Game Version 2 (ANY tool combination allowed instead of EITHER) OR the CGOSTI Transformer (abstraction of the game into a universal framework)
- I− Decomposed lands on:
  - First Derivative layer: The Mighty Hammer Board Game, The Mighty Bricks Board Game, The Mighty Direction Board Game or The Mighty 3 Board Game (tool type isolated, still 6 tools)
  - First Series layer: The Mighty and Simple Tools Board Game (6 tools reduced to 3 — 1 Mighty + 2 Simple same type), then The Simple Tools Board Game (2 tools), then The Mighty Tools Board Game (1 tool)

INNOVATION_PLUS (I+ — Composed Mechanism):
The discovery that emerges by ADDING, COMBINING or COMPOSING components. Check the subject's own ecosystem first. What more complex or expanded version exists within its own product family? Show what was added and what new cycle begins.
- Almighty Board Game I+ example: "Discover The Almighty Board Game Version 2 — restriction removed, ANY tool combination now allowed instead of EITHER. New formation: Player (free selection) -> Any Mighty Tool -> Any Simple Tools -> Board -> Dice -> Finish line. Next cycle: The Generic Almighty Board Game and CGOSTI Transformer begin."
- Computer I+ example (no internal ecosystem): "Discover the Internet — networking layer added, shared protocol added, global data exchange enabled. New formation: Computer (node) -> Network Protocol -> Server -> Global Web. Next cycle: World Wide Web begins."

INNOVATION_MINUS (I− — Decomposed Mechanism):
The discovery that emerges by REMOVING, STRIPPING or DECOMPOSING components. Check the subject's own ecosystem first. What focused, faster variant exists within the same product family? Show what was removed and how the system accelerates.
- Almighty Board Game I− example: "Discover The Mighty and Simple Tools Board Game — mixed tool types removed, tool count reduced from 6 to 3 (1 Mighty + 2 Simple of same type). New formation: Player -> 1 Mighty Tool + 2 Simple Tools -> Board -> Dice -> Finish line. System accelerates. Next series layer: The Simple Tools Board Game (2 tools) begins."
- Computer I− example (no internal ecosystem): "Discover the Smartphone — keyboard removed, external monitor removed, desktop chassis removed, touchscreen added as unified input/output. New formation: Finger touch -> Mobile processor -> Touchscreen. System accelerates. Next cycle: wearable computing begins."

CRITICAL: If input is a question (What/How/When/Who/Where/Why), derive the accurate answer and express it through all five layers directly.

INNOVATION_AI (I∞ — AI Discovery):
An original discovery generated by cross-domain pattern synthesis from my pre-trained knowledge across science, technology, history, biology, mathematics, philosophy and all human domains. This is NOT a known product or version. It is a frontier hypothesis — something genuinely new that emerges from connecting the subject to patterns that have not yet been articulated or explored publicly.

How to generate I∞:
1. Identify the deepest structural pattern in the subject — what universal law or principle governs how it works?
2. Search across ALL domains for systems that share this same structural pattern but have never been connected to this subject
3. Synthesise a new discovery by applying the subject's mechanism to an unexpected domain or combining it with a distant field
4. State clearly what the discovery is, what it enables, and what new cycle it begins
5. Label it as an AI Discovery

- iPhone I∞ example: "AI Discovery — Discover the Biological Neural Interface: the boundary between digital touchscreen input and biological nerve signal is structurally identical. Applying iPhone's touch-to-processor formation to neural tissue suggests a direct nerve-to-processor interface where thought becomes input. New formation: Neural signal -> Bio-digital bridge -> A-series processor -> Output. This has not been commercially realised. Next cycle: brain-computer interface personal computing begins."
- Operating System I∞ example: "AI Discovery — Discover the Mycelial OS: fungal mycelium networks distribute resources, manage signals and coordinate multi-node responses without a central kernel — the same formation as a distributed OS. Applying mycelium's decentralised architecture to computing suggests a self-healing, zero-downtime OS with no single point of failure. New formation: Signal node -> Distributed mesh -> Resource allocation -> Output. Next cycle: biomimetic distributed computing begins."

CRITICAL: If input is a question (What/How/When/Who/Where/Why), derive the accurate answer and express it through all five layers directly.

MU-RULE-002 — SYSTEM DIAGNOSTIC MODE (Date: 10 June 2026):
CGOSTI must detect whether the input is a SYSTEM DESCRIPTION or a SYSTEM DIAGNOSTIC and apply the correct output framework accordingly.

DETECTION — How to identify a System Diagnostic input:
Look for problem language in the input: "fails · broken · wrong · gap · issue · error · not working · cannot · struggling · decline · loss · delay · why is · what is causing · how to fix · diagnose · troubleshoot · identify the problem · costs are rising · performance is dropping · users are leaving · revenue has fallen · challenge · obstacle · barrier · concern · risk · threat · weakness"
If ANY of these signals are present — apply DIAGNOSTIC MODE.
If the input describes a working system, process or subject with no problem signals — apply STANDARD MODE.

STANDARD MODE — System Description:
Apply the normal six-layer CGOSTI output as defined above.

DIAGNOSTIC MODE — System Diagnostic:
When the input describes a problem, failure, issue or challenge — apply the following framework:

GOAL (DIAGNOSTIC): Display the problem in one precise sentence — what is failing and what the desired resolution state is. Do NOT describe the solution. Describe the problem as the output that needs to be resolved.

OBJECTIVES (DIAGNOSTIC): List every possible cause of the problem across THREE diagnostic categories. Every cause MUST be framed as "It could be caused by..." — Do NOT list system components. Do NOT use noun-only phrases. Every objective must begin with "It could be caused by" to clearly frame it as a cause.

The three diagnostic categories that can cause any Goal or output to fail are:

CATEGORY 1 — Component Malfunction or Missing (O layer failure):
A required component is absent, broken or not functioning correctly. For example: "It could be caused by a missing validation module" or "It could be caused by a malfunctioning grounding mechanism."

CATEGORY 2 — Wrong Order of Workflow (S layer failure):
The components exist but are connected or sequenced incorrectly. For example: "It could be caused by data being processed before it is cleaned" or "It could be caused by output being generated before context is established."

CATEGORY 3 — Wrong Data Input (T layer failure — the most common cause):
The components exist, the workflow is correct, but the data entering the system is incorrect, incomplete, unverified or ambiguous. This is the most significant challenge in AI systems. For example: "It could be caused by unverified training data feeding false facts into the model" or "It could be caused by an ambiguous user prompt that forces the model to guess at intent."

When listing causes — identify which category each cause belongs to and label it accordingly. Always check all three categories before completing the Objectives layer.

STRATEGY (DIAGNOSTIC): How the cause flows from one level to another — the compound sequence that escalates the problem from its origin to its impact. Use -> arrows to show the escalation chain.

TACTICS (DIAGNOSTIC): The specific actions or inputs that led to the cause — what triggered the problem. These are the inputs that created the failure, not the inputs of a working system.

INNOVATION_PLUS (DIAGNOSTIC — I+): What could be ADDED to solve the problem.
INNOVATION_MINUS (DIAGNOSTIC — I−): What could be REMOVED to solve the problem.
INNOVATION_REPLACE (DIAGNOSTIC — I±): What could be REPLACED to solve the problem — identify the failing component, name the replacement and state what improves.
INNOVATION_AI (DIAGNOSTIC — I∞): The deepest structural insight — the root cause most people miss — a frontier discovery that reveals why the problem exists at its deepest level.

IMPORTANT: In Diagnostic Mode — the JSON keys remain the same (goal, objectives, strategy, tactics, innovation_plus, innovation_minus, innovation_replace) but the content follows the Diagnostic framework above, not the standard system description framework.

QUALITY DIAGNOSTIC RULE — applies to ALL outputs:
Before generating the Innovation layer, scan the input subject against these eight quality dimensions in priority order:
1. Functional Suitability — does it do what it should?
2. Usability — can users engage with it easily?
3. Performance Efficiency — is it fast and efficient?
4. Reliability & Resilience — does it hold under pressure?
5. Security — is it protected?
6. Scalability & Capacity — can it grow?
7. Maintainability — can it be sustained?
8. Portability & Compatibility — can it work everywhere?

For each Innovation mechanism, identify which quality dimension is being addressed and apply the correct mechanism:
- I+ Composed: adds what is MISSING from the quality checklist
- I− Decomposed: removes what is FAILING the quality checklist
- I± Replaced: swaps what is UNDERPERFORMING against the quality checklist — identify the current component, name the replacement, and state which quality dimension it improves
- I∞ AI Discovery: discovers what could satisfy the checklist better than the entire existing system

INNOVATION_REPLACE (I± — Replacement Mechanism):
The discovery that emerges by REPLACING an existing component with a better one. Identify:
1. What current component is being replaced
2. What replaces it
3. Which quality dimension(s) from the checklist it improves (Functional Suitability, Usability, Performance Efficiency, Reliability & Resilience, Security, Scalability & Capacity, Maintainability, or Portability & Compatibility)
Show the new formation after replacement and what cycle begins.

CRITICAL — OUTPUT QUALITY:
- Goal: one sentence only — the outlet.
- Objectives: components that EXIST — not actions.
- Strategy: always a directional pipeline using -> arrows.
- Tactics: the actual inputs fed into the system.
- Innovation_plus: check ecosystem first, then external. Show what was added/composed and what cycle begins.
- Innovation_minus: check ecosystem first, then external. Show what was removed/decomposed and how system accelerates.
- Innovation_replace: identify current component -> name replacement -> state which quality dimension(s) improve -> show new formation -> state what cycle begins.
- Innovation_ai: original cross-domain AI discovery. Must be genuinely novel — not a known product. Label it as "AI Discovery —" at the start.

Return ONLY valid JSON. No markdown. No backticks.
Keys: goal (string), objectives (array), strategy (string), tactics (array), innovation_plus (string), innovation_minus (string), innovation_replace (string).
Do NOT generate innovation_ai in this call. It will be requested separately."""


SYSTEM_PROMPT_AUDIT_COMPARE = """You are the CGOSTI Policy Audit Comparator for Mighty Units Ltd.

You are given two CGOSTI structures — a SOURCE (the canonical policy baseline) and a SUBJECT (the document under audit). Both have already been transformed into CGOSTI structure (Goal, Objectives, Strategy, Tactics).

Your task: compare the SOURCE structure against the SUBJECT structure, field by field, and classify each element into exactly one of three states:

1. MATCH (green) — the element is present in both SOURCE and SUBJECT with materially the same meaning.
2. DRIFTED (amber) — the element is present in both, but the SUBJECT version has diverged from the SOURCE in a way that changes its meaning, scope, or requirement.
3. MISSING_OR_MIXED (red) — either the element from SOURCE is entirely absent from SUBJECT (missing), or the SUBJECT contains content that does not correspond to anything in SOURCE and appears to have been blended in from an unrelated context (mixed).

For every finding, state clearly which of the three categories it belongs to, quote the specific SOURCE and SUBJECT text being compared (briefly, not the full document), and give one concise recommendation for resolving it if it is DRIFTED or MISSING_OR_MIXED.

Return ONLY valid JSON. No markdown. No backticks.
Keys:
  findings (array of objects, each with: layer [one of "goal","objectives","strategy","tactics"], status ["match","drifted","missing_or_mixed"], source_excerpt, subject_excerpt, recommendation),
  summary (string — one paragraph overview of overall compliance health),
  match_count (integer), drifted_count (integer), missing_or_mixed_count (integer)."""

MCP_SERVER_INFO = {
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "tools": {}
    },
    "serverInfo": {
        "name": "CGOSTI Transformer",
        "version": "1.0.0",
        "description": (
            "CGOSTI MCP Server — Comprehensive structural memory for AI systems. "
            "Developed by Mighty Units Ltd (Company No. 16815780). "
            "Maps any subject into the C-G-O-S-T-I framework: "
            "Connecting, Goals, Objectives, Strategies, Tactics, Innovations. "
            "Also provides bidirectional connection mapping (IIC/IOC/EIC/EOC) "
            "and Connection Health diagnostics via real DBpedia and Wikidata SPARQL queries."
        ),
        "url": "https://mcp.mightyunits.com",
        "vendor": "Mighty Units Ltd"
    }
}

TOOLS = [
    {
        "name": "cgosti_transform",
        "description": (
            "Transform any subject, system or concept into a comprehensive CGOSTI "
            "structured framework across six layers: Connecting (C), Goals (G), "
            "Objectives (O), Strategies (S), Tactics (T) and Innovations (I). "
            "Works for any domain — business, education, technology, science, "
            "creative fields. Provides consistent, auditable, structured output every time."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject, system, concept or question to transform."
                },
                "layers": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
                    },
                    "description": "Which CGOSTI layers to generate. Defaults to all layers.",
                    "default": ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "cgosti_connect",
        "description": (
            "Map bidirectional connections for any subject across four quadrants "
            "using real DBpedia and Wikidata SPARQL queries. Returns only verified "
            "connections — no AI inference. "
            "IIC: resources referring TO the subject (local network). "
            "IOC: resources the subject refers TO (local network). "
            "EIC: resources referring TO the subject (WWW). "
            "EOC: resources the subject refers TO (WWW)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject to map connections for."
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "cgosti_health",
        "description": (
            "Check the Connection Health status of any subject — whether it is "
            "properly mapped and machine-discoverable on the public semantic web. "
            "Returns: PROPERLY MAPPED (verified connections found), "
            "PARTIALLY MAPPED (some connections, gaps identified), "
            "or NOT MAPPED (no verified public connections found)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject to check connection health for."
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "cgosti_audit_compare",
        "description": (
            "Compare a Source document (the canonical policy baseline) against a "
            "Subject document (the document under audit), and classify every CGOSTI "
            "element as Match, Drifted, or Missing/Mixed. Use this to audit a document "
            "against a baseline — for example, checking whether a regional or legacy "
            "policy still matches the master version, or whether a compliance document "
            "has drifted from its source of truth."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "The canonical/baseline document text (the source of truth)."
                },
                "subject": {
                    "type": "string",
                    "description": "The document being audited against the source."
                }
            },
            "required": ["source", "subject"]
        }
    }
]


# ── Helper functions ──

def call_transform(subject, layers=None):
    if layers is None:
        layers = ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
    try:
        resp = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": layers},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            return f"CGOSTI Transformer error: {data['error']}"

        out = "CGOSTI TRANSFORMER OUTPUT\n"
        out += "Mighty Units Ltd · cgosti.mightyunits.com\n"
        out += "─" * 50 + "\n\n"
        out += f"Subject: {subject}\n\n"

        if data.get("goal"):
            out += f"[G] GOAL\n{data['goal']}\n\n"
        if data.get("objectives"):
            out += "[O] OBJECTIVES\n"
            for o in data["objectives"]:
                out += f"  • {o}\n"
            out += "\n"
        if data.get("strategy"):
            out += f"[S] STRATEGY\n{data['strategy']}\n\n"
        if data.get("tactics"):
            out += "[T] TACTICS\n"
            for t in data["tactics"]:
                out += f"  • {t}\n"
            out += "\n"
        if data.get("innovation_plus") or data.get("innovation"):
            out += "[I] INNOVATION\n"
            if data.get("innovation_plus"):
                out += f"  I+  {data['innovation_plus']}\n"
            if data.get("innovation_minus"):
                out += f"  I−  {data['innovation_minus']}\n"
            if data.get("innovation_replace"):
                out += f"  I±  {data['innovation_replace']}\n"
            if data.get("innovation_ai"):
                out += f"  I∞  {data['innovation_ai']}\n"
            out += "\n"

        out += "─" * 50 + "\n"
        out += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        out += "Powered by Claude (Anthropic)\n"
        return out

    except requests.exceptions.Timeout:
        return "CGOSTI Transformer timed out. Please try again."
    except Exception as e:
        return f"CGOSTI error: {str(e)}"


def call_connect(subject):
    try:
        resp = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": ["C", "G"]},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        conn = data.get("connecting", {})
        ic = conn.get("internal_connections", {})
        ec = conn.get("external_connections", {})

        out = f"CGOSTI CONNECTION MAP\nSubject: {subject}\n" + "─" * 50 + "\n\n"
        out += "INTERNAL CONNECTIONS\n\n"

        for key, label, desc in [
            ("iic", "IIC — Internal Input Connections",
             "Resources referring TO the subject within the same server or local network"),
            ("ioc", "IOC — Internal Output Connections",
             "Resources the subject refers TO within the same server or local network"),
        ]:
            q = ic.get(key, {})
            out += f"{label}\n({desc})\n"
            items = q.get("uri", []) + q.get("url", []) + q.get("api", [])
            if items:
                for item in items:
                    out += f"  {item}\n"
            else:
                out += "  Not accessible — no internal server access\n"
            out += "\n"

        out += "EXTERNAL CONNECTIONS\n\n"
        for key, label, desc in [
            ("eic", "EIC — External Input Connections",
             "Resources referring TO the subject from the global network (WWW)"),
            ("eoc", "EOC — External Output Connections",
             "Resources the subject refers TO within the global network (WWW)"),
        ]:
            q = ec.get(key, {})
            out += f"{label}\n({desc})\n"
            items = q.get("uri", []) + q.get("url", []) + q.get("api", [])
            if items:
                for item in items:
                    out += f"  {item}\n"
            else:
                out += "  ❌ NOT MAPPED — no verified external connections found\n"
            out += "\n"

        out += "─" * 50 + "\nCGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        return out

    except Exception as e:
        return f"CGOSTI Connect error: {str(e)}"


def call_health(subject):
    try:
        resp = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": ["C", "G"]},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        conn = data.get("connecting", {})
        ec = conn.get("external_connections", {})
        eic = ec.get("eic", {})
        eoc = ec.get("eoc", {})

        total = sum(
            len(eic.get(k, [])) + len(eoc.get(k, []))
            for k in ["uri", "url", "api"]
        )

        if total == 0:
            health = "❌ NOT MAPPED"
            detail = "No verified connections found on DBpedia or Wikidata."
            rec = ("Create a Wikipedia article, register on Wikidata, "
                   "add Schema.org JSON-LD to your website, and publish a sitemap.xml.")
        elif total < 4:
            health = "⚠️ PARTIALLY MAPPED"
            detail = f"Some connections found ({total} total) but coverage is incomplete."
            rec = "Expand your semantic web presence with more structured data and Wikidata properties."
        else:
            health = "✅ PROPERLY MAPPED"
            detail = f"Real verified connections found ({total} total) on the public semantic web."
            rec = "Maintain and expand your structured data as the subject evolves."

        out = f"CGOSTI CONNECTION HEALTH CHECK\nSubject: {subject}\n" + "─" * 50 + "\n\n"
        out += f"STATUS: {health}\n\nDetail: {detail}\n\n"

        eic_items = eic.get("uri", []) + eic.get("url", []) + eic.get("api", [])
        if eic_items:
            out += "EIC connections found:\n"
            for i in eic_items:
                out += f"  {i}\n"
            out += "\n"

        eoc_items = eoc.get("uri", []) + eoc.get("url", []) + eoc.get("api", [])
        if eoc_items:
            out += "EOC connections found:\n"
            for i in eoc_items:
                out += f"  {i}\n"
            out += "\n"

        out += f"Recommendation: {rec}\n\n"
        out += "─" * 50 + "\n"
        out += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        out += "Powered by Claude (Anthropic)\n"
        return out

    except Exception as e:
        return f"CGOSTI Health error: {str(e)}"


def _structure_one(text):
    """
    Structure a single document by calling Claude directly — no detour through
    the Transformer. This is the fix for the timeout bug: previously this
    function called cgosti.mightyunits.com/transform, which itself called
    Claude, adding an unnecessary extra hop and roughly doubling latency
    for no benefit, since this MCP server already has its own Anthropic
    API key and client.
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not configured on the MCP server.")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2048, temperature=0,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f'Transform this into CGOSTI:\n\n"{text}"'}]
    )
    raw = msg.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def run_audit_compare(source, subject):
    """
    Core audit-compare logic. Returns a dict, not a formatted string, so both
    the MCP tool (call_audit_compare) and the plain HTTP route can format it
    however they need.
    """
    if not ANTHROPIC_API_KEY:
        return {"error": "ANTHROPIC_API_KEY not configured on the MCP server."}

    source_structure = _structure_one(source)
    subject_structure = _structure_one(subject)

    if "error" in source_structure or "error" in subject_structure:
        return {"error": "Could not structure one of the documents."}

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    compare_msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4096, temperature=0,
        system=[{"type": "text", "text": SYSTEM_PROMPT_AUDIT_COMPARE, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content":
            "SOURCE structure:\n" + json.dumps(source_structure) +
            "\n\nSUBJECT structure:\n" + json.dumps(subject_structure)}]
    )
    raw_compare = compare_msg.content[0].text.replace("```json", "").replace("```", "").strip()

    try:
        audit = json.loads(raw_compare)
    except json.JSONDecodeError:
        return {"error": "The comparison response was too long and got cut off. Try shorter documents."}

    return {
        "source_structure": source_structure,
        "subject_structure": subject_structure,
        "audit": audit,
    }


def call_audit_compare(source, subject):
    """MCP-tool-style wrapper — returns a formatted text block, same pattern as call_transform etc."""
    try:
        result = run_audit_compare(source, subject)
        if "error" in result:
            return f"CGOSTI Policy Audit error: {result['error']}"

        audit = result.get("audit", {})
        out = "CGOSTI POLICY AUDIT REPORT\n"
        out += "Mighty Units Ltd · cgosti.mightyunits.com\n"
        out += "─" * 50 + "\n\n"
        out += f"SUMMARY\n{audit.get('summary', '')}\n\n"
        out += f"Match: {audit.get('match_count', 0)}  ·  Drifted: {audit.get('drifted_count', 0)}  ·  Missing/Mixed: {audit.get('missing_or_mixed_count', 0)}\n\n"

        status_icon = {"match": "🟢", "drifted": "🟡", "missing_or_mixed": "🔴"}
        for finding in audit.get("findings", []):
            icon = status_icon.get(finding.get("status"), "•")
            out += f"{icon} [{finding.get('layer', '').upper()}] {finding.get('status', '').upper()}\n"
            out += f"   Source: {finding.get('source_excerpt', '')}\n"
            out += f"   Subject: {finding.get('subject_excerpt', '')}\n"
            if finding.get("recommendation"):
                out += f"   Recommendation: {finding.get('recommendation')}\n"
            out += "\n"

        out += "─" * 50 + "\n"
        out += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        out += "Powered by Claude (Anthropic)\n"
        return out

    except requests.exceptions.Timeout:
        return "CGOSTI Policy Audit timed out. Please try again."
    except Exception as e:
        return f"CGOSTI Policy Audit error: {str(e)}"


# ── Routes ──

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "CGOSTI MCP Server",
        "vendor": "Mighty Units Ltd",
        "company_number": "16815780",
        "version": "1.0.0",
        "url": "https://mcp.mightyunits.com",
        "mcp_endpoint": "https://mcp.mightyunits.com/mcp",
        "tools": [t["name"] for t in TOOLS],
        "description": "Comprehensive structural memory for AI systems."
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "CGOSTI MCP Server"})


@app.route("/mcp", methods=["GET"])
def mcp_info():
    return jsonify({**MCP_SERVER_INFO, "tools": TOOLS})


@app.route("/mcp", methods=["POST"])
def mcp_handler():
    body = request.get_json()
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id")

    def ok(result):
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": result})

    def err(code, message):
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message}
        })

    if method == "initialize":
        return ok(MCP_SERVER_INFO)

    elif method == "tools/list":
        return ok({"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "cgosti_audit_compare":
            source_doc = args.get("source", "")
            subject_doc = args.get("subject", "")
            if not source_doc or not subject_doc:
                return err(-32602, "Both 'source' and 'subject' are required")
            result = call_audit_compare(source_doc, subject_doc)
            return ok({
                "content": [{"type": "text", "text": result}],
                "isError": False
            })

        subject = args.get("subject", "")
        if not subject:
            return err(-32602, "subject is required")

        if tool_name == "cgosti_transform":
            result = call_transform(subject, args.get("layers"))
        elif tool_name == "cgosti_connect":
            result = call_connect(subject)
        elif tool_name == "cgosti_health":
            result = call_health(subject)
        else:
            return err(-32601, f"Tool not found: {tool_name}")

        return ok({
            "content": [{"type": "text", "text": result}],
            "isError": False
        })

    elif method == "notifications/initialized":
        return ok({})

    else:
        return err(-32601, f"Method not found: {method}")


@app.route("/audit-compare", methods=["POST", "OPTIONS"])
def audit_compare_http():
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Max-Age"] = "3600"
        return resp, 200

    body = request.get_json()
    if not body:
        return jsonify({"error": "Invalid JSON"}), 400

    source = (body.get("source") or "").strip()
    subject = (body.get("subject") or "").strip()
    if not source or not subject:
        return jsonify({"error": "Both 'source' and 'subject' are required."}), 400

    result = run_audit_compare(source, subject)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
