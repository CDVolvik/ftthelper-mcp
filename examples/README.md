# Example client configs

Copy the file for your client, replace `ftth_mcp_YOUR_TOKEN_HERE` with a token
you minted, and restart the client.

| File | Client | Where it goes |
|---|---|---|
| `claude-desktop.json` | Claude Desktop | `claude_desktop_config.json` — Settings → Developer → Edit Config |
| `claude-code.json` | Claude Code | `.mcp.json` in your project root, or `~/.claude.json` globally |
| `cursor.json` | Cursor | `.cursor/mcp.json` in your project, or `~/.cursor/mcp.json` globally |
| `codex.toml` | Codex CLI | `~/.codex/config.toml` |

`cursor.json` and `claude-desktop.json` are byte-identical on purpose, so you can
copy either one without editing it. `claude-code.json` differs in two ways: it
needs `"type": "http"`, and it reads the token from the environment instead of
storing it — see below.

## Keep the `www.`

Every URL here is `https://www.fantasytabletophelper.com/api/mcp`. That is not
cosmetic. The bare domain redirects to `www`, and HTTP clients deliberately drop
the `Authorization` header when a redirect changes origin — so pointing a client
at the apex, with the `www.` left off, strips your token in transit and a
**valid** token comes back `401 Invalid or missing MCP token`.

If you get a 401 with a token you just minted, check the URL before you suspect
the token.

## The token is a credential

Do not commit a filled-in config.

`claude-code.json` is the safer pattern to copy: it references
`${FTTHELPER_MCP_TOKEN}` rather than embedding the secret, so the file stays
safe to commit and the token lives in your environment.

```bash
export FTTHELPER_MCP_TOKEN='ftth_mcp_...'          # macOS / Linux
```

```powershell
[Environment]::SetEnvironmentVariable('FTTHELPER_MCP_TOKEN','ftth_mcp_...','User')   # Windows
```

Restart the client afterwards so it picks the variable up. If you have already
pasted a token into a file you no longer control, revoke it on `/account/mcp`.
