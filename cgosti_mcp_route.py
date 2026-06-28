"""
CGOSTI MCP Server — HTTP/SSE transport for Railway deployment
Add this as a route to your existing app.py

Usage:
  1. Copy cgosti_mcp_server.py alongside app.py
  2. Add the route below to app.py
  3. Push to Railway

The MCP server will be accessible at:
  https://cgosti.mightyunits.com/mcp
"""

# ── Add this import to app.py ──
# from cgosti_mcp_route import cgosti_mcp_blueprint

# ── Add this line after app = Flask(__name__) ──
# app.register_blueprint(cgosti_mcp_blueprint)

from flask import Blueprint, request, Response, jsonify
import json
import requests
import time

cgosti_mcp_blueprint = Blueprint("cgosti_mcp", __name__)

CGOSTI_API_BASE = "https://cgosti.mightyunits.com"

MCP_SERVER_INFO = {
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "tools": {}
    },
    "serverInfo": {
        "name": "CGOSTI Transformer",
        "version": "1.0.0",
        "description": "CGOSTI Transformer MCP Server — Comprehensive structural memory for AI systems. Developed by Mighty Units Ltd (Company No. 16815780). Maps any subject into the C-G-O-S-T-I framework: Connecting, Goals, Objectives, Strategies, Tactics, Innovations.",
        "url": "https://cgosti.mightyunits.com/mcp",
        "vendor": "Mighty Units Ltd"
    }
}

TOOLS = [
    {
        "name": "cgosti_transform",
        "description": "Transform any subject, system or concept into a comprehensive CGOSTI structured framework across six layers: Connecting (C), Goals (G), Objectives (O), Strategies (S), Tactics (T) and Innovations (I). Works for any domain — business, education, technology, science, creative fields. Provides consistent, auditable, structured output every time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject, system, concept or question to transform into a CGOSTI structure."
                },
                "layers": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]},
                    "description": "Which CGOSTI layers to generate. Defaults to all layers if not specified.",
                    "default": ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "cgosti_connect",
        "description": "Map the bidirectional connections for any subject across four quadrants using real DBpedia and Wikidata SPARQL queries. Returns only verified connections — no AI inference. IIC: resources referring TO the subject (local network). IOC: resources the subject refers TO (local network). EIC: resources referring TO the subject (WWW). EOC: resources the subject refers TO (WWW).",
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
        "description": "Check the Connection Health status of any subject — whether it is properly mapped and machine-discoverable on the public semantic web. Returns: PROPERLY MAPPED (verified connections found), PARTIALLY MAPPED (some connections, gaps identified), or NOT MAPPED (no verified public connections). Uses real DBpedia and Wikidata data.",
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
    }
]


def call_cgosti_transform(subject, layers=None):
    if layers is None:
        layers = ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
    try:
        resp = requests.post(
            f"{CGOSTI_API_BASE}/transform",
            json={"input": subject, "layers": layers},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            return f"CGOSTI Transformer error: {data['error']}"

        output = "CGOSTI TRANSFORMER OUTPUT\nMighty Units Ltd · cgosti.mightyunits.com\n" + "─" * 50 + "\n\n"
        output += f"Subject: {subject}\n\n"

        if data.get("goal"):
            output += f"[G] GOAL\n{data['goal']}\n\n"
        if data.get("objectives"):
            output += "[O] OBJECTIVES\n" + "".join(f"  • {o}\n" for o in data["objectives"]) + "\n"
        if data.get("strategy"):
            output += f"[S] STRATEGY\n{data['strategy']}\n\n"
        if data.get("tactics"):
            output += "[T] TACTICS\n" + "".join(f"  • {t}\n" for t in data["tactics"]) + "\n"
        if data.get("innovation_plus") or data.get("innovation"):
            output += "[I] INNOVATION\n"
            if data.get("innovation_plus"): output += f"  I+ {data['innovation_plus']}\n"
            if data.get("innovation_minus"): output += f"  I− {data['innovation_minus']}\n"
            if data.get("innovation_replace"): output += f"  I± {data['innovation_replace']}\n"
            if data.get("innovation_ai"): output += f"  I∞ {data['innovation_ai']}\n"
            output += "\n"

        output += "─" * 50 + "\nCGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\nPowered by Claude (Anthropic)\n"
        return output
    except Exception as e:
        return f"CGOSTI error: {str(e)}"


def call_cgosti_connect(subject):
    try:
        resp = requests.post(
            f"{CGOSTI_API_BASE}/transform",
            json={"input": subject, "layers": ["C", "G"]},
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        conn = data.get("connecting", {})
        ic = conn.get("internal_connections", {})
        ec = conn.get("external_connections", {})

        output = f"CGOSTI CONNECTION MAP\nSubject: {subject}\n" + "─" * 50 + "\n\n"
        output += "INTERNAL CONNECTIONS\n\n"

        for key, label, desc in [
            ("iic", "IIC — Internal Input Connections", "Resources referring TO the subject within the same server or local network"),
            ("ioc", "IOC — Internal Output Connections", "Resources the subject refers TO within the same server or local network")
        ]:
            q = ic.get(key, {})
            output += f"{label}\n({desc})\n"
            items = q.get("uri", []) + q.get("url", []) + q.get("api", [])
            if items:
                for item in items: output += f"  {item}\n"
            else:
                output += "  Not accessible — no internal server access\n"
            output += "\n"

        output += "EXTERNAL CONNECTIONS\n\n"
        for key, label, desc in [
            ("eic", "EIC — External Input Connections", "Resources referring TO the subject from the global network (WWW)"),
            ("eoc", "EOC — External Output Connections", "Resources the subject refers TO within the global network (WWW)")
        ]:
            q = ec.get(key, {})
            output += f"{label}\n({desc})\n"
            items = q.get("uri", []) + q.get("url", []) + q.get("api", [])
            if items:
                for item in items: output += f"  {item}\n"
            else:
                output += "  ❌ NOT MAPPED — no verified external connections found\n"
            output += "\n"

        output += "─" * 50 + "\nCGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        return output
    except Exception as e:
        return f"CGOSTI Connect error: {str(e)}"


def call_cgosti_health(subject):
    try:
        resp = requests.post(
            f"{CGOSTI_API_BASE}/transform",
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
        total = sum(len(eic.get(k, [])) + len(eoc.get(k, [])) for k in ["uri", "url", "api"])

        if total == 0:
            health = "❌ NOT MAPPED"
            detail = "No verified connections found on DBpedia or Wikidata."
            rec = "Create a Wikipedia article, register on Wikidata, add Schema.org JSON-LD to your website, and publish a sitemap.xml."
        elif total < 4:
            health = "⚠️ PARTIALLY MAPPED"
            detail = f"Some connections found ({total} total) but coverage is incomplete."
            rec = "Expand your semantic web presence with more structured data and Wikidata properties."
        else:
            health = "✅ PROPERLY MAPPED"
            detail = f"Real verified connections found ({total} total) on the public semantic web."
            rec = "Maintain and expand your structured data as the subject evolves."

        output = f"CGOSTI CONNECTION HEALTH CHECK\nSubject: {subject}\n" + "─" * 50 + "\n\n"
        output += f"STATUS: {health}\n\nDetail: {detail}\n\n"

        eic_items = eic.get("uri", []) + eic.get("url", []) + eic.get("api", [])
        if eic_items:
            output += f"EIC connections found:\n" + "".join(f"  {i}\n" for i in eic_items) + "\n"

        eoc_items = eoc.get("uri", []) + eoc.get("url", []) + eoc.get("api", [])
        if eoc_items:
            output += f"EOC connections found:\n" + "".join(f"  {i}\n" for i in eoc_items) + "\n"

        output += f"Recommendation: {rec}\n\n"
        output += "─" * 50 + "\nCGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\nPowered by Claude (Anthropic)\n"
        return output
    except Exception as e:
        return f"CGOSTI Health error: {str(e)}"


@cgosti_mcp_blueprint.route("/mcp", methods=["GET"])
def mcp_info():
    """MCP server info endpoint."""
    return jsonify({
        **MCP_SERVER_INFO,
        "tools": TOOLS
    })


@cgosti_mcp_blueprint.route("/mcp", methods=["POST"])
def mcp_handler():
    """Handle MCP JSON-RPC requests."""
    body = request.get_json()
    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id")

    def ok(result):
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": result})

    def err(code, message):
        return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

    if method == "initialize":
        return ok(MCP_SERVER_INFO)

    elif method == "tools/list":
        return ok({"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "cgosti_transform":
            result = call_cgosti_transform(
                subject=args.get("subject", ""),
                layers=args.get("layers", None)
            )
        elif tool_name == "cgosti_connect":
            result = call_cgosti_connect(subject=args.get("subject", ""))
        elif tool_name == "cgosti_health":
            result = call_cgosti_health(subject=args.get("subject", ""))
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
