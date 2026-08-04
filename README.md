# Fantasy Tabletop Helper — MCP server

Connect Claude Desktop, Cursor, Codex, or any MCP-capable client to your
tabletop campaigns, and ask questions about your own world in plain language.

> *"Which NPCs in Westruun belong to a religion, and which of them have my party
> already met?"*

This repository holds the connection docs and example client configs. The server
itself is hosted — it runs inside [fantasytabletophelper.com](https://fantasytabletophelper.com),
so there is nothing to install, clone, or keep running.

- **Endpoint:** `https://www.fantasytabletophelper.com/api/mcp` — keep the `www.`, see [below](#keep-the-www)
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

### 1. Create a token

On the site, go to **Account → AI Tool Access** (`/account/mcp`), name the token
after the tool you are connecting, and press **Create token**.

The token appears once, beginning `ftth_mcp_`. **Copy it then.** Only a hash is
stored, so it cannot be shown again. If you lose one, revoke it and make another.

### 2. Configure your client

Ready-to-edit files are in [`examples/`](examples). Claude Desktop, for
instance:

```json
{
  "mcpServers": {
    "ftthelper": {
      "url": "https://www.fantasytabletophelper.com/api/mcp",
      "headers": { "Authorization": "Bearer ftth_mcp_YOUR_TOKEN_HERE" }
    }
  }
}
```

Restart the client. `ftthelper` should appear in its tool list.

#### Keep the `www.`

It is not cosmetic. The bare domain redirects to `www`, and HTTP clients drop the
`Authorization` header whenever a redirect changes origin — sensibly, since they
cannot know the new host deserves your credentials. Point a client at
`https://fantasytabletophelper.com/api/mcp` and the token is stripped in transit,
so the server sees an anonymous request and answers `401 Invalid or missing MCP
token` for a perfectly good token.

### 3. Ask it something

> "List my campaigns, then find every religion in the Westruun one."

---

## Revoking a token

Press **Revoke** next to it on **Account → AI Tool Access**. It takes effect on
that client's next request. Revoke any token you have pasted somewhere you no
longer control.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `404` | Wrong path, or the server is switched off on this deployment. |
| `401` **on a token you just made** | Almost always the URL: the bare domain instead of `www.`, which strips the token. Check that before suspecting the token. |
| `401` | Token is wrong, revoked, or expired. Make a new one. |
| `503` | We could not open a session for your account. Usually transient; retry. |
| `403` | Your plan is not Hero. |
| `405` on a GET | Expected. The server is POST-only; your client should be using POST. |
| Connects, but every tool call returns an error | A server-side configuration problem. Contact support — the server logs these. |
| A tool returns an empty list | Usually genuine: you have no campaigns yet, or the search matched nothing. |

The last two rows are worth keeping apart. An empty list is an answer; an error
is a fault.

## Licence

Docs and example configs: [MIT](LICENSE). The hosted service has its own
[terms](https://fantasytabletophelper.com/terms).
