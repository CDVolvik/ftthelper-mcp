# Fantasy Tabletop Helper — MCP server

Connect Claude Desktop, Cursor, Codex, or any MCP-capable client to your
tabletop campaigns, and ask questions about your own world in plain language.

> *"Which NPCs in Westruun belong to a religion, and which of them have my party
> already met?"*

This repository holds the connection docs and example client configs. The server
itself is hosted — it runs inside [fantasytabletophelper.com](https://fantasytabletophelper.com),
so there is nothing to install, clone, or keep running.

- **Endpoint:** `https://fantasytabletophelper.com/api/mcp`
- **Transport:** stateless Streamable HTTP, POST only
- **Access:** read-only, Hero plan
- **Source:** closed. The app is a commercial product; this repo is the client-side half.

---

## Read-only, and scoped to you

Every tool is read-only. Nothing an AI client does over this connection can
create, edit, or delete anything in your campaign.

More importantly, the server queries the database **as you**, not as an
administrator. Your row-level security policies are what decide the answer, so
the MCP surface can only ever show what the website would show you when logged
in:

| | Who sees it |
|---|---|
| Party notes | Campaign members |
| DM-only notes | The DM of that campaign, or whoever wrote them |
| Private notes | Only their author |
| Codex entries | Members of that campaign; non-canon entries only for the DM |

If you are a player, pointing an AI client at your campaign cannot surface your
DM's secrets. That is enforced in the database, not in application code.

## Tools

| Tool | Returns |
|---|---|
| `list_campaigns` | Your campaigns, and your role in each |
| `get_campaign` | One campaign's details |
| `list_sessions` | Sessions, most recently played first |
| `search_codex` | NPCs, locations, items, lore, religions, cultures, groups |
| `get_subject` | One codex entry in full, with its relationships |
| `get_session_notes` | Notes from a single session |

Factions and guilds are stored as `kind: "group"` — there is no separate
`faction` kind.

---

## Setup

### 1. Mint a token

Signed in to the site, from the same browser:

```bash
curl -X POST https://fantasytabletophelper.com/api/mcp/tokens \
  -H 'content-type: application/json' \
  -b "<your browser session cookie>" \
  -d '{"label":"Claude Desktop"}'
```

The response carries a `token` beginning `ftth_mcp_`. **Copy it now.** Only a
hash is stored, so it cannot be shown again. If you lose one, revoke it and mint
another.

### 2. Configure your client

Ready-to-edit files are in [`examples/`](examples). Claude Desktop, for
instance:

```json
{
  "mcpServers": {
    "ftthelper": {
      "url": "https://fantasytabletophelper.com/api/mcp",
      "headers": { "Authorization": "Bearer ftth_mcp_YOUR_TOKEN_HERE" }
    }
  }
}
```

Restart the client. `ftthelper` should appear in its tool list.

### 3. Ask it something

> "List my campaigns, then find every religion in the Westruun one."

---

## Revoking a token

```bash
curl -X DELETE 'https://fantasytabletophelper.com/api/mcp/tokens?id=<token id>' \
  -b "<your browser session cookie>"
```

Revocation is immediate. Revoke any token you have pasted somewhere you no
longer control.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `404` | The MCP server is not enabled on this deployment yet. |
| `401` | Token is wrong, revoked, or expired. Mint a new one. |
| `403` | Your plan is not Hero. |
| `405` on a GET | Expected. The server is POST-only; your client should be using POST. |
| Connects, but every tool call returns an error | A server-side configuration problem. Contact support — the server logs these. |
| A tool returns an empty list | Usually genuine: you have no campaigns yet, or the search matched nothing. |

The last two rows are worth keeping apart. An empty list is an answer; an error
is a fault.

## Licence

Docs and example configs: [MIT](LICENSE). The hosted service has its own
[terms](https://fantasytabletophelper.com/terms).
