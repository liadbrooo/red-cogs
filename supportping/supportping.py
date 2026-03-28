from redbot.core import commands, Config
import time

class SupportPing(commands.Cog):
    """Pingt ein Team, wenn jemand den Support-Warteraum betritt."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=987654321)

        default_guild = {
            "voice_channel": None,
            "text_channel": None,
            "role": None,
            "enabled": True,
            "cooldown": 30,
            "only_if_empty": False,
            "last_ping": 0
        }

        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not after.channel:
            return

        guild = member.guild
        data = await self.config.guild(guild).all()

        if not data["enabled"]:
            return

        if after.channel.id != data["voice_channel"]:
            return

        # Nur wenn wirklich neu gejoint
        if before.channel and before.channel.id == after.channel.id:
            return

        # Nur pingen wenn Channel vorher leer war
        if data["only_if_empty"]:
            if len(after.channel.members) > 1:
                return

        # Cooldown
        now = time.time()
        if now - data["last_ping"] < data["cooldown"]:
            return

        text_channel = guild.get_channel(data["text_channel"])
        role_id = data["role"]

        if text_channel and role_id:
            await text_channel.send(
                f"<@&{role_id}> 🔔 {member.mention} wartet im Support!"
            )
            await self.config.guild(guild).last_ping.set(now)

    # --------------------
    # ⚙️ Commands
    # --------------------

    @commands.group()
    @commands.admin()
    async def supportping(self, ctx):
        """SupportPing Einstellungen"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Nutze Subcommands wie setvoice, settext, setrole...")

    @supportping.command()
    async def setvoice(self, ctx, channel):
        """Setze den Voice Channel"""
        await self.config.guild(ctx.guild).voice_channel.set(channel.id)
        await ctx.send(f"✅ Voice Channel gesetzt: {channel.mention}")

    @supportping.command()
    async def settext(self, ctx, channel):
        """Setze den Text Channel"""
        await self.config.guild(ctx.guild).text_channel.set(channel.id)
        await ctx.send(f"✅ Text Channel gesetzt: {channel.mention}")

    @supportping.command()
    async def setrole(self, ctx, role):
        """Setze die Rolle"""
        await self.config.guild(ctx.guild).role.set(role.id)
        await ctx.send(f"✅ Rolle gesetzt: {role.mention}")

    @supportping.command()
    async def toggle(self, ctx):
        """Ein/Aus"""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        await ctx.send(f"🔁 Aktiv: {not current}")

    @supportping.command()
    async def cooldown(self, ctx, seconds: int):
        """Cooldown in Sekunden"""
        await self.config.guild(ctx.guild).cooldown.set(seconds)
        await ctx.send(f"⏱ Cooldown gesetzt auf {seconds}s")

    @supportping.command()
    async def onlyifempty(self, ctx, value: bool):
        """Nur pingen wenn Channel leer war"""
        await self.config.guild(ctx.guild).only_if_empty.set(value)
        await ctx.send(f"👥 Nur wenn leer: {value}")

    @supportping.command()
    async def status(self, ctx):
        """Zeigt aktuelle Einstellungen"""
        data = await self.config.guild(ctx.guild).all()

        await ctx.send(
            f"📊 **SupportPing Status**\n"
            f"Enabled: {data['enabled']}\n"
            f"Cooldown: {data['cooldown']}s\n"
            f"Only if empty: {data['only_if_empty']}\n"
            f"Voice Channel: {data['voice_channel']}\n"
            f"Text Channel: {data['text_channel']}\n"
            f"Role: {data['role']}"
        )
