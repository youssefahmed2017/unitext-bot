# Unitext Discord Bot

A tiny Discord bot that turns text into Unicode typography:

```text
/unitext font:bold message:Hello world
```

Result:

```text
𝐇𝐞𝐥𝐥𝐨 𝐰𝐨𝐫𝐥𝐝
```

The visible channel message is sent through a Discord webhook using the invoking member's display name and avatar. The slash-command interaction is answered ephemerally, so the channel is left with the generated text rather than a public bot response.

## Included styles

`bold`, `italic`, `bold_italic`, `script`, `fraktur`, `double`, `monospace`, `circled`, `small_caps`, `superscript`, `subscript`, `upside_down`, `greek`

Run `/unitext_fonts` in a server to see the list.

## Setup

### 1. Create the Discord app

Create an application in the Discord Developer Portal, add a bot user, and copy its token.

Invite it with the `bot` and `applications.commands` scopes. The bot needs **Manage Webhooks** in the channels where `/unitext` is used. It does not need the privileged Message Content, Members, or Presence intents.

### 2. Install

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Put your token in `.env`:

```env
DISCORD_TOKEN=...
DEV_GUILD_ID=123456789012345678
WEBHOOK_NAME=Unitext
```

`DEV_GUILD_ID` is optional but strongly recommended during development because guild commands are available much faster than global commands.

### 3. Run

```bash
python -m unitext
```

Or:

```bash
python -m unitext.bot
```

## How the message flow works

```text
User
  |
  | /unitext font:bold message:Hello
  v
Discord Interaction
  |
  | private/ephemeral acknowledgement
  v
Unitext bot
  |
  | Unicode transform
  | H -> 𝐇, e -> 𝐞, ...
  v
Channel webhook
  |
  | username = invoking member's display name
  | avatar   = invoking member's avatar
  v
𝐇𝐞𝐥𝐥𝐨
```

This is a real webhook message, not a self-bot/user-account automation trick.

## Notes

Unicode styles are not actual Discord font settings. They replace characters with Unicode code points that have stylized glyphs. Coverage is therefore imperfect: some styles only have a subset of Latin characters, and Discord/client fonts may render unsupported characters differently.

The `greek` style is intentionally a Greek-ish visual mapping, not a full transliteration engine.

Discord message content is limited, so Unitext rejects input that would result in more than 2,000 characters.

## License

MIT
