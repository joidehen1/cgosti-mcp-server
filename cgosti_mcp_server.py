"""
CGOSTI MCP Server
Mighty Units Ltd · Company No. 16815780 · cgosti.mightyunits.com

Exposes the CGOSTI Transformer as an MCP server so Claude and other
AI systems can call it natively — adding comprehensive structural memory
(CGOSTI memory) alongside Claude's existing vector memory.

Four tools:
  cgosti_transform     — maps any subject into the full C-G-O-S-T-I framework
  cgosti_audit_compare — compares a Source document against a Subject document, classifying findings as Match/Drifted/Missing-or-Mixed
  cgosti_connect       — maps the IIC/IOC/EIC/EOC connection quadrants for any subject
  cgosti_health        — returns the Connection Health status for any subject
"""

import json
import requests
from mcp.server.fastmcp import FastMCP

# ── Server definition ──
mcp = FastMCP(
    name="CGOSTI Transformer",
    instructions="""
You have access to the CGOSTI Transformer — a comprehensive structured framework
developed by Mighty Units Ltd (Company No. 16815780).

CGOSTI stands for:
  C — Connecting  (interior connection: O, S, T, I connected to G)
  G — Goals       (the desired output of any subject or system)
  O — Objectives  (the components required to reach the goal)
  S — Strategies  (the workflow order of those components)
  T — Tactics     (the inputs and actions required)
  I — Innovations (how to innovate the goal — I+, I-, I±, I∞)

Use these tools whenever a user asks you to:
  - Structure, map or analyse any subject, system or concept
  - Understand what a subject connects to
  - Check whether a subject is properly mapped on the semantic web
  - Generate a comprehensive framework for any domain
  - Audit a document against a baseline or policy, checking for drift, gaps or mismatches

The CGOSTI framework works for any subject — business, education, technology,
science, creative fields, or any other domain.
""",
)

CGOSTI_API = "https://cgosti.mightyunits.com"


# ── Tool 1: cgosti_transform ──
@mcp.tool()
def cgosti_transform(
    subject: str,
    layers: list[str] = None,
) -> str:
    """
    Transform any subject, system or concept into a comprehensive CGOSTI
    structured framework.

    Args:
        subject: The subject, system, concept or question to transform.
        layers: Which layers to generate. Options: "G", "O", "S", "T",
                "I+", "I-", "I±", "I∞". Defaults to all layers.

    Returns:
        A comprehensive structured CGOSTI framework for the subject.
    """
    if layers is None:
        layers = ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]

    try:
        response = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": layers},
            timeout=60,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return f"CGOSTI Transformer error: {data['error']}"

        # Format the output as structured text
        output = f"CGOSTI TRANSFORMER OUTPUT\n"
        output += f"Mighty Units Ltd · cgosti.mightyunits.com\n"
        output += "─" * 50 + "\n\n"
        output += f"Subject: {subject}\n\n"

        if data.get("goal"):
            output += f"[G] GOAL — The desired output\n{data['goal']}\n\n"

        if data.get("objectives"):
            output += f"[O] OBJECTIVES — Tools & components\n"
            for obj in data["objectives"]:
                output += f"  • {obj}\n"
            output += "\n"

        if data.get("strategy"):
            output += f"[S] STRATEGY — Workflow & architecture\n{data['strategy']}\n\n"

        if data.get("tactics"):
            output += f"[T] TACTICS — Inputs & actions\n"
            for tac in data["tactics"]:
                output += f"  • {tac}\n"
            output += "\n"

        if data.get("innovation_plus") or data.get("innovation"):
            output += f"[I] INNOVATION\n"
            if data.get("innovation_plus"):
                output += f"  I+ Composed: {data['innovation_plus']}\n"
            if data.get("innovation_minus"):
                output += f"  I− Decomposed: {data['innovation_minus']}\n"
            if data.get("innovation_replace"):
                output += f"  I± Replaced: {data['innovation_replace']}\n"
            if data.get("innovation_ai"):
                output += f"  I∞ AI Discovery: {data['innovation_ai']}\n"
            output += "\n"

        output += "─" * 50 + "\n"
        output += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        output += "Powered by Claude (Anthropic)\n"

        return output

    except requests.exceptions.Timeout:
        return "CGOSTI Transformer timed out. The server may be starting up — please try again in a moment."
    except requests.exceptions.ConnectionError:
        return "Could not connect to CGOSTI Transformer at cgosti.mightyunits.com. Please check the server is running."
    except Exception as e:
        return f"CGOSTI Transformer error: {str(e)}"


# ── Tool 2: cgosti_audit_compare ──
@mcp.tool()
def cgosti_audit_compare(source: str, subject: str) -> str:
    """
    Compare a Source document (the canonical policy baseline) against a
    Subject document (the document under audit), and classify every CGOSTI
    element as Match, Drifted, or Missing/Mixed.

    Use this when a user wants to audit a document against a baseline —
    for example, checking whether a regional or legacy policy still matches
    the master version, or whether a compliance document has drifted from
    its source of truth.

    Args:
        source: The canonical/baseline document text (the source of truth).
        subject: The document being audited against the source.

    Returns:
        A structured audit report — findings classified as Match (green),
        Drifted (amber), or Missing/Mixed (red), with recommendations.
    """
    try:
        response = requests.post(
            f"{CGOSTI_API}/audit-compare",
            json={"source": source, "subject": subject},
            timeout=90,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return f"CGOSTI Policy Audit error: {data['error']}"

        audit = data.get("audit", {})
        output = "CGOSTI POLICY AUDIT REPORT\n"
        output += "Mighty Units Ltd · cgosti.mightyunits.com\n"
        output += "─" * 50 + "\n\n"
        output += f"SUMMARY\n{audit.get('summary', '')}\n\n"
        output += f"Match: {audit.get('match_count', 0)}  ·  Drifted: {audit.get('drifted_count', 0)}  ·  Missing/Mixed: {audit.get('missing_or_mixed_count', 0)}\n\n"

        status_icon = {"match": "🟢", "drifted": "🟡", "missing_or_mixed": "🔴"}
        for finding in audit.get("findings", []):
            icon = status_icon.get(finding.get("status"), "•")
            output += f"{icon} [{finding.get('layer', '').upper()}] {finding.get('status', '').upper()}\n"
            output += f"   Source: {finding.get('source_excerpt', '')}\n"
            output += f"   Subject: {finding.get('subject_excerpt', '')}\n"
            if finding.get("recommendation"):
                output += f"   Recommendation: {finding.get('recommendation')}\n"
            output += "\n"

        output += "─" * 50 + "\n"
        output += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        output += "Powered by Claude (Anthropic)\n"
        return output

    except requests.exceptions.Timeout:
        return "CGOSTI Policy Audit timed out. The comparison of two full documents can take longer — please try again."
    except requests.exceptions.ConnectionError:
        return "Could not connect to CGOSTI Transformer at cgosti.mightyunits.com. Please check the server is running."
    except Exception as e:
        return f"CGOSTI Policy Audit error: {str(e)}"


# ── Tool 3: cgosti_connect ──
@mcp.tool()
def cgosti_connect(subject: str) -> str:
    """
    Map the bidirectional connections for any subject across four quadrants:
      IIC — Internal Input Connections (resources referring TO the subject, local network)
      IOC — Internal Output Connections (resources the subject refers TO, local network)
      EIC — External Input Connections (resources referring TO the subject, WWW)
      EOC — External Output Connections (resources the subject refers TO, WWW)

    Uses real DBpedia and Wikidata SPARQL queries — returns only verified connections.

    Args:
        subject: The subject to map connections for.

    Returns:
        The four-quadrant connection map with URI, URL and API connections.
    """
    try:
        response = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": ["C", "G"]},
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        conn = data.get("connecting", {})
        ic = conn.get("internal_connections", {})
        ec = conn.get("external_connections", {})

        output = f"CGOSTI CONNECTION MAP\n"
        output += f"Subject: {subject}\n"
        output += "─" * 50 + "\n\n"

        # Internal connections
        output += "INTERNAL CONNECTIONS\n\n"
        iic = ic.get("iic", {})
        output += f"IIC — Internal Input Connections\n"
        output += f"(Resources referring TO the subject within the same server or local network)\n"
        uris = iic.get("uri", [])
        urls = iic.get("url", [])
        apis = iic.get("api", [])
        if uris or urls or apis:
            for u in uris: output += f"  URI: {u}\n"
            for u in urls: output += f"  URL: {u}\n"
            for a in apis: output += f"  API: {a}\n"
        else:
            output += "  Not accessible — no internal server access\n"

        output += "\n"
        ioc = ic.get("ioc", {})
        output += f"IOC — Internal Output Connections\n"
        output += f"(Resources the subject refers TO within the same server or local network)\n"
        uris = ioc.get("uri", [])
        urls = ioc.get("url", [])
        apis = ioc.get("api", [])
        if uris or urls or apis:
            for u in uris: output += f"  URI: {u}\n"
            for u in urls: output += f"  URL: {u}\n"
            for a in apis: output += f"  API: {a}\n"
        else:
            output += "  Not accessible — no internal server access\n"

        output += "\nEXTERNAL CONNECTIONS\n\n"
        eic = ec.get("eic", {})
        output += f"EIC — External Input Connections\n"
        output += f"(Resources referring TO the subject from the global network — WWW)\n"
        uris = eic.get("uri", [])
        urls = eic.get("url", [])
        apis = eic.get("api", [])
        if uris or urls or apis:
            for u in uris: output += f"  URI: {u}\n"
            for u in urls: output += f"  URL: {u}\n"
            for a in apis: output += f"  API: {a}\n"
        else:
            output += "  ❌ NOT MAPPED — no verified external connections found\n"

        output += "\n"
        eoc = ec.get("eoc", {})
        output += f"EOC — External Output Connections\n"
        output += f"(Resources the subject refers TO within the global network — WWW)\n"
        uris = eoc.get("uri", [])
        urls = eoc.get("url", [])
        apis = eoc.get("api", [])
        if uris or urls or apis:
            for u in uris: output += f"  URI: {u}\n"
            for u in urls: output += f"  URL: {u}\n"
            for a in apis: output += f"  API: {a}\n"
        else:
            output += "  ❌ NOT MAPPED — no verified external connections found\n"

        output += "\n" + "─" * 50 + "\n"
        output += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"

        return output

    except Exception as e:
        return f"CGOSTI Connect error: {str(e)}"


# ── Tool 4: cgosti_health ──
@mcp.tool()
def cgosti_health(subject: str) -> str:
    """
    Check the Connection Health status of any subject — whether it is
    properly mapped and machine-discoverable on the public semantic web.

    Returns one of three statuses:
      ✅ PROPERLY MAPPED   — real verified connections found on DBpedia/Wikidata
      ⚠️ PARTIALLY MAPPED  — some connections exist, gaps identified
      ❌ NOT MAPPED        — no verified public connections found

    Args:
        subject: The subject to check connection health for.

    Returns:
        Connection Health status with details of what was found and what is missing.
    """
    try:
        response = requests.post(
            f"{CGOSTI_API}/transform",
            json={"input": subject, "layers": ["C", "G"]},
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        conn = data.get("connecting", {})
        ec = conn.get("external_connections", {})
        eic = ec.get("eic", {})
        eoc = ec.get("eoc", {})

        eic_total = len(eic.get("uri", [])) + len(eic.get("url", [])) + len(eic.get("api", []))
        eoc_total = len(eoc.get("uri", [])) + len(eoc.get("url", [])) + len(eoc.get("api", []))
        total = eic_total + eoc_total

        if total == 0:
            health = "❌ NOT MAPPED"
            detail = "No verified connections found on DBpedia or Wikidata. The subject has no public presence on the semantic web."
            recommendation = "To become properly mapped: create a Wikipedia article, register on Wikidata, add Schema.org JSON-LD structured data to your website, and publish a sitemap.xml."
        elif total < 4:
            health = "⚠️ PARTIALLY MAPPED"
            detail = f"Some connections found ({total} total) but coverage is incomplete."
            recommendation = "Expand your semantic web presence by adding more structured data, Schema.org markup and Wikidata properties."
        else:
            health = "✅ PROPERLY MAPPED"
            detail = f"Real verified connections found ({total} total) on the public semantic web."
            recommendation = "Maintain and expand your structured data as the subject evolves."

        output = f"CGOSTI CONNECTION HEALTH CHECK\n"
        output += f"Subject: {subject}\n"
        output += "─" * 50 + "\n\n"
        output += f"STATUS: {health}\n\n"
        output += f"Detail: {detail}\n\n"

        if eic_total > 0:
            output += f"EIC (External Input) — {eic_total} connections found:\n"
            for u in eic.get("uri", []): output += f"  URI: {u}\n"
            for u in eic.get("url", []): output += f"  URL: {u}\n"
            for a in eic.get("api", []): output += f"  API: {a}\n"
            output += "\n"

        if eoc_total > 0:
            output += f"EOC (External Output) — {eoc_total} connections found:\n"
            for u in eoc.get("uri", []): output += f"  URI: {u}\n"
            for u in eoc.get("url", []): output += f"  URL: {u}\n"
            for a in eoc.get("api", []): output += f"  API: {a}\n"
            output += "\n"

        output += f"Recommendation: {recommendation}\n\n"
        output += "─" * 50 + "\n"
        output += "CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026\n"
        output += "Powered by Claude (Anthropic)\n"

        return output

    except Exception as e:
        return f"CGOSTI Health error: {str(e)}"


# ── Entry point ──
if __name__ == "__main__":
    mcp.run(transport="stdio")
