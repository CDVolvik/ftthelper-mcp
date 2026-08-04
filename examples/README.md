# Example client configs

Copy the file for your client, replace `ftth_mcp_YOUR_TOKEN_HERE` with a token
you minted, and restart the client.

| File | Client | Where it goes |
|---|---|---|
| `claude-desktop.json` | Claude Desktop | `claude_desktop_config.json` — Settings → Developer → Edit Config |
| `cursor.json` | Cursor | `.cursor/mcp.json` in your project, or `~/.cursor/mcp.json` globally |
| `codex.toml` | Codex CLI | `~/.codex/config.toml` |

The JSON clients take the same shape, so `cursor.json` and
`claude-desktop.json` are byte-identical on purpose. They are kept as separate
files so you can copy one without editing it.

Do not commit a filled-in config. The token is a credential.
