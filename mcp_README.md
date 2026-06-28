# CGOSTI MCP Server
**Mighty Units Ltd · Company No. 16815780**

CGOSTI MCP Server exposes the CGOSTI Transformer as a Model Context Protocol (MCP)
server — adding comprehensive structural memory (CGOSTI memory) to Claude and other
AI systems alongside their existing vector memory.

## What is CGOSTI?

CGOSTI is a six-layer framework discovered through the development of The Almighty
Board Game. The same pattern repeated consistently across every stage — from first
concept to finished product — across multiple game series and derivatives.

**C — Connecting** · Interior connection: O, S, T, I connected to G
**G — Goals** · The desired output of any subject or system
**O — Objectives** · The components required to reach the goal
**S — Strategies** · The workflow order of those components
**T — Tactics** · The inputs and actions required
**I — Innovations** · How to innovate the goal (I+, I-, I±, I∞)

## MCP Endpoint

```
https://mcp.mightyunits.com/mcp
```

## Three Tools

### cgosti_transform
Transform any subject into a comprehensive CGOSTI structured framework.

```json
{
  "name": "cgosti_transform",
  "arguments": {
    "subject": "Machine Learning",
    "layers": ["G", "O", "S", "T", "I+", "I-", "I±", "I∞"]
  }
}
```

### cgosti_connect
Map bidirectional connections for any subject using real DBpedia and Wikidata
SPARQL queries. Returns IIC, IOC, EIC and EOC connection quadrants.

```json
{
  "name": "cgosti_connect",
  "arguments": {
    "subject": "Google"
  }
}
```

### cgosti_health
Check whether any subject is properly mapped on the public semantic web.
Returns: ✅ PROPERLY MAPPED / ⚠️ PARTIALLY MAPPED / ❌ NOT MAPPED

```json
{
  "name": "cgosti_health",
  "arguments": {
    "subject": "Mighty Units Ltd"
  }
}
```

## Deployment

### Railway
1. Create a new Railway project from this repo
2. Railway auto-detects Python and the Procfile
3. Set environment variable if needed: `PORT` (auto-set by Railway)
4. Point DNS: `mcp.mightyunits.com` → Railway URL (CNAME)

### Local development
```bash
pip install -r requirements.txt
python app.py
```

Server runs at: http://localhost:5001

## Architecture

```
Claude / AI System
       ↓
CGOSTI MCP Server (mcp.mightyunits.com)
       ↓
CGOSTI Transformer API (cgosti.mightyunits.com)
       ↓
DBpedia SPARQL + Wikidata SPARQL + Anthropic Claude API
```

## Contact

Osayuki Idehen — Founder & CEO, Mighty Units Ltd
joidehen@mightyunits.com · cgosti.mightyunits.com

CGOSTI FRAMEWORK © MIGHTY UNITS LTD 2026 · POWERED BY CLAUDE (ANTHROPIC)
