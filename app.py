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
    """Structure a single document via the Transformer's existing /transform endpoint."""
    resp = requests.post(
        f"{CGOSTI_API}/transform",
        json={"input": text, "layers": ["G", "O", "S", "T"]},
        timeout=60,
        headers={"Content-Type": "application/json"}
    )
    resp.raise_for_status()
    return resp.json()


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
        return jsonify({"status": "ok"}), 200

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
