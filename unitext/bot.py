from __future__ import annotations

import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from .fonts import STYLES, normalize_style, style_names, transform, visible_name

# Short, mixed-case-and-digit sample used to preview each style in the
# autocomplete dropdown, so users recognize the look instead of guessing
# from a label name alone.
PREVIEW_TEXT = "Aa1"

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")
WEBHOOK_NAME = os.getenv("WEBHOOK_NAME", "Unitext")[:80]
MAX_INPUT = 1900

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Put it in .env or your environment."
    )


class UnitextClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._webhook_cache: dict[int, discord.Webhook] = {}

    async def setup_hook(self) -> None:
        if DEV_GUILD_ID:
            guild = discord.Object(id=int(DEV_GUILD_ID))
            self.tree.copy_global_to(guild=guild)

            synced = await self.tree.sync(guild=guild)

            print(
                f"[unitext] synced {len(synced)} command(s) "
                f"to DEV_GUILD_ID={DEV_GUILD_ID}"
            )
        else:
            synced = await self.tree.sync()
            print(f"[unitext] synced {len(synced)} global command(s)")

    async def on_ready(self) -> None:
        print(
            f"[unitext] logged in as {self.user} "
            f"(id={self.user.id if self.user else 'unknown'})"
        )

        print(f"[unitext] styles: {', '.join(style_names())}")

    async def on_message(self, message: discord.Message) -> None:
        """Fast path: `!<style> text` in a normal message, no slash command
        round-trip. We delete the trigger message and re-post the
        transformed text via the channel's webhook, so there's no
        interaction ACK / "thinking" UI involved at all."""

        if message.author.bot or not message.guild:
            return

        if not message.content.startswith("!"):
            return

        prefix, _, rest = message.content.partition(" ")
        style = normalize_style(prefix[1:])
        rest = rest.strip()

        if style is None or not rest:
            return

        channel = message.channel

        if not isinstance(channel, discord.TextChannel):
            return

        me = message.guild.me

        if me is None or not channel.permissions_for(me).manage_messages:
            return

        transformed = transform(rest, style)

        if len(transformed) > 2000:
            return

        try:
            webhook = await self.ensure_webhook(channel, me)
        except (PermissionError, discord.HTTPException):
            return

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            return

        try:
            await webhook.send(
                transformed,
                username=message.author.display_name[:80],
                avatar_url=message.author.display_avatar.url,
                wait=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.HTTPException:
            pass

    async def ensure_webhook(
        self,
        channel: discord.TextChannel,
        me: discord.Member,
    ) -> discord.Webhook:
        """Find or create Unitext's incoming webhook in a text channel."""

        perms = channel.permissions_for(me)

        if not perms.view_channel:
            raise PermissionError(
                "I can't view this channel.\n"
                f"Effective permissions: "
                f"View Channel={perms.view_channel}, "
                f"Send Messages={perms.send_messages}, "
                f"Manage Webhooks={perms.manage_webhooks}, "
                f"Administrator={perms.administrator}"
            )

        if not perms.manage_webhooks:
            raise PermissionError(
                "I need the **Manage Webhooks** permission in this channel.\n"
                f"Effective permissions: "
                f"View Channel={perms.view_channel}, "
                f"Send Messages={perms.send_messages}, "
                f"Manage Webhooks={perms.manage_webhooks}, "
                f"Administrator={perms.administrator}\n"
                f"Channel: #{channel.name}"
            )

        cached = self._webhook_cache.get(channel.id)
        if cached is not None:
            return cached

        hooks = await channel.webhooks()

        for hook in hooks:
            if (
                hook.user
                and self.user
                and hook.user.id == self.user.id
                and hook.name == WEBHOOK_NAME
            ):
                self._webhook_cache[channel.id] = hook
                return hook

        webhook = await channel.create_webhook(
            name=WEBHOOK_NAME,
            reason="Unitext output webhook",
        )
        self._webhook_cache[channel.id] = webhook
        return webhook


client = UnitextClient()


async def font_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    current = current.lower().strip()

    matches = [
        key
        for key, (label, _) in STYLES.items()
        if current in key or current in label.lower()
    ]

    choices = []

    for key in matches[:25]:
        label, func = STYLES[key]
        preview = f"{label}: {func(PREVIEW_TEXT)}"[:100]
        choices.append(app_commands.Choice(name=preview, value=key))

    return choices


@client.tree.command(
    name="unitext",
    description="Send a message using Unicode typography.",
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    font="Unicode style to use",
    message="The message to transform",
)
@app_commands.autocomplete(font=font_autocomplete)
async def unitext(
    interaction: discord.Interaction,
    font: str,
    message: str,
) -> None:
    if len(message) > MAX_INPUT:
        await interaction.response.send_message(
            f"Your message is too long. Keep it under {MAX_INPUT} "
            "characters so Unicode expansion stays below Discord's limit.",
            ephemeral=True,
        )
        return

    style = normalize_style(font)

    if style is None:
        choices = ", ".join(style_names())

        await interaction.response.send_message(
            f"Unknown style `{font}`. Available styles: `{choices}`",
            ephemeral=True,
        )
        return

    transformed = transform(message, style)

    if len(transformed) > 2000:
        await interaction.response.send_message(
            "That transformation produced more than Discord's "
            "2000-character message limit. Try a shorter message.",
            ephemeral=True,
        )
        return

    guild = interaction.guild

    if guild is None:
        # DM or user-install context: there's no webhook to spoof identity
        # through (Discord has no DM webhooks, and a user-installed app has
        # no guild permissions), so just reply visibly as Unitext itself.
        await interaction.response.send_message(transformed)
        return

    channel = interaction.channel

    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(
            "Unitext currently works in server text channels only.",
            ephemeral=True,
        )
        return

    # Only pay for a defer ("thinking...") round-trip when we know we're
    # about to make a slow network call: fetching our own member object,
    # or a webhook cache miss (listing/creating a webhook). On the common
    # warm-cache path everything below is fast enough to answer within
    # Discord's 3-second interaction window without one.
    deferred = False

    me = guild.me

    if me is None:
        await interaction.response.defer(ephemeral=True)
        deferred = True

        try:
            me = await guild.fetch_member(client.user.id)
        except discord.HTTPException:
            await interaction.followup.send(
                "I couldn't fetch my member information from Discord.",
                ephemeral=True,
            )
            return

    if not deferred and channel.id not in client._webhook_cache:
        await interaction.response.defer(ephemeral=True)
        deferred = True

    async def respond(content: str) -> None:
        if deferred:
            await interaction.followup.send(content, ephemeral=True)
        else:
            await interaction.response.send_message(content, ephemeral=True)

    try:
        webhook = await client.ensure_webhook(channel, me)

        avatar_url = interaction.user.display_avatar.url
        username = interaction.user.display_name[:80]

        await webhook.send(
            transformed,
            username=username,
            avatar_url=avatar_url,
            wait=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    except PermissionError as exc:
        await respond(str(exc))
        return

    except discord.Forbidden:
        await respond(
            "Discord denied the webhook operation.\n"
            "Make sure Unitext has **Manage Webhooks** in this exact "
            "channel and that there isn't an explicit channel/category deny."
        )
        return

    except discord.HTTPException as exc:
        await respond(
            f"Discord rejected the output message (`HTTP {exc.status}`). "
            "Check the bot's channel permissions and try again."
        )
        return

    await respond(f"Sent with **{visible_name(style)}**.")


@client.tree.command(
    name="unitext_fonts",
    description="Show all Unitext styles.",
)
@app_commands.guild_only()
async def unitext_fonts(interaction: discord.Interaction) -> None:
    lines = [
        f"`{key}` — {label}: {func(PREVIEW_TEXT)}"
        for key, (label, func) in STYLES.items()
    ]

    await interaction.response.send_message(
        "\n".join(lines),
        ephemeral=True,
    )


def main() -> None:
    client.run(TOKEN)


if __name__ == "__main__":
    main()
