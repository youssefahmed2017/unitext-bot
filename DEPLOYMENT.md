# Deployment

## Why not Vercel

Unitext uses `discord.py`'s **gateway** connection: a persistent outbound
WebSocket to Discord that stays open 24/7 to receive events (slash-command
interactions, and every `MESSAGE_CREATE` for the `!style text` fast path).

Vercel (like Cloudflare Workers) runs **serverless functions**: short-lived,
request-triggered, no facility for a long-running background process. There
is no way to keep a gateway connection open there, with Python or any other
runtime. So the current bot cannot run on Vercel as-is, full stop — this
isn't a config/tuning problem, it's a structural mismatch between what the
bot needs and what the platform provides.

### What *would* run on Vercel

Discord supports a separate integration model: **HTTP-only Interactions**.
You register an "Interactions Endpoint URL" in the Developer Portal, and
Discord POSTs each slash-command invocation directly to that URL. Your
handler verifies the request's Ed25519 signature and replies with JSON —
no gateway connection involved. Vercel's Python runtime can host that.

If ported to this model:

- `/unitext` could work, rebuilt as a stateless HTTP handler.
- The `!style text` fast path **cannot be ported** — it only exists because
  the bot watches every normal channel message via the gateway. The
  Interactions webhook model never sees ordinary messages, only interaction
  payloads. There is no HTTP-only equivalent for "watch messages and react
  to them."
- `fonts.py`'s transform tables port over unchanged (they're pure functions,
  no framework dependency).
- Needs new code: Ed25519 signature verification, a route that parses
  Discord's interaction JSON, and webhook-send logic via plain HTTP calls
  (no `discord.py` client object available in this model).

This is a real rewrite, not a deploy-config change, and it trades away a
shipped feature. Nothing described above has been built — this section is
scoping only, for if that trade is ever worth making.

## What actually works today: a persistent host

The bot needs a host that keeps one Python process running continuously.
Already set up for this in the repo:

- `requirements.txt` at the repo root — most hosts auto-install from it.
- `main.py` at the repo root — a plain-script entry point (`from
  unitext.bot import main`) for panels that run a file directly rather than
  `python -m unitext`. Verified working locally.
- Config is entirely environment-variable driven (`DISCORD_TOKEN`,
  `DEV_GUILD_ID`, `WEBHOOK_NAME`) via `os.getenv`, so it doesn't matter
  whether the host injects them directly or you hand it a `.env` file —
  both work identically.

### Free hosts evaluated (no credit card)

| Provider | RAM | Renewal | Always-on claim | Notes |
|---|---|---|---|---|
| **Bot-Hosting.net** | 256 MB | every 4 days | explicit, free tier included | Best fit found; public pool is often full |
| Pella | 100 MB | unclear | not stated | Weakest specs, uptime unconfirmed |
| FPS.ms | 128 MB | every 24h | conditional on renewal | Tight renewal window |
| HYEHOST | not listed | every 30 days | paid plans only | Free-tier always-on unconfirmed |
| Railway | — | 30-day trial, then $1/mo credit | n/a | Not viable long-term for a 24/7 process |

Whichever is used, the panel setup is the same shape (most of these are
white-label Pterodactyl panels):

1. Clone/upload this repo (exclude `.venv`, never upload the real `.env`).
2. Set the entry/startup file to `main.py`.
3. Set environment variables in the host's panel: `DISCORD_TOKEN` (required),
   `DEV_GUILD_ID` and `WEBHOOK_NAME` (optional).
4. In the Discord Developer Portal, confirm **Message Content Intent** is
   enabled on the Bot tab — required for the `!style text` fast path. Not
   confirmed to be permitted on every free tier; check after first boot.
5. Grant the bot **Manage Webhooks** (required) and **Manage Messages**
   (required only for the `!style text` fast path, to delete the trigger
   message) in the channels it's used in.
