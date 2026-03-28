import time
import discord
from redbot.core import commands, Config

__version__ = "1.2.0"  # Cog-Version

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

    # --------------------
    # Listener
    # --------------------
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

        if before.channel and before.channel.id == after.channel.id:
            return

        # Optional: nur wenn Channel vorher leer war
        if data["only_if_empty"] and len(after.channel.members) > 1:
            return

        # Cooldown prüfen
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
    # Commands
    # --------------------
    @commands.group()
    @commands.admin()
    async def supportping(self, ctx):
        """SupportPing Einstellungen"""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Nutze Subcommands: setvoice, settext, setrole, toggle, cooldown, "
                "onlyifempty, status, version"
            )

    # --- Set Voice Channel ---
    @supportping.command()
    async def setvoice(self, ctx, channel):
        """Setze den Voice Channel per Mention oder ID"""
        vc = None
        if isinstance(channel, discord.VoiceChannel):
            vc = channel
        else:
            try:
                channel_id = int(str(channel).replace("<#", "").replace(">", ""))
                vc = ctx.guild.get_channel(channel_id)
                if not isinstance(vc, discord.VoiceChannel):
                    return await ctx.send("❌ Die ID ist kein Voice Channel")
            except:
                return await ctx.send("❌ Ungültiger Channel")
        await self.config.guild(ctx.guild).voice_channel.set(vc.id)
        await ctx.send(f"✅ Voice Channel gesetzt: {vc.mention}")

    # --- Set Text Channel ---
    @supportping.command()
    async def settext(self, ctx, channel):
        """Setze den Text Channel per Mention oder ID"""
        tc = None
        if isinstance(channel, discord.TextChannel):
            tc = channel
        else:
            try:
                channel_id = int(str(channel).replace("<#", "").replace(">", ""))
                tc = ctx.guild.get_channel(channel_id)
                if not isinstance(tc, discord.TextChannel):
                    return await ctx.send("❌ Die ID ist kein Text Channel")
            except:
                return await ctx.send("❌ Ungültiger Channel")
        await self.config.guild(ctx.guild).text_channel.set(tc.id)
        await ctx.send(f"✅ Text Channel gesetzt: {tc.mention}")

    # --- Set Role ---
    @supportping.command()
    async def setrole(self, ctx, role):
        """Setze die Rolle per Mention oder ID"""
        r = None
        if isinstance(role, discord.Role):
            r = role
        else:
            try:
                role_id = int(str(role).replace("<@&", "").replace(">", ""))
                r = discord.utils.get(ctx.guild.roles, id=role_id)
                if not r:
                    return await ctx.send("❌ Ungültige Rolle")
            except:
                return await ctx.send("❌ Ungültige Rolle")
        await self.config.guild(ctx.guild).role.set(r.id)
        await ctx.send(f"✅ Rolle gesetzt: {r.mention}")

    # --- Toggle ---
    @supportping.command()
    async def toggle(self, ctx):
        """Ein/Aus"""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        await ctx.send(f"🔁 Aktiv: {not current}")

    # --- Cooldown ---
    @supportping.command()
    async def cooldown(self, ctx, seconds: int):
        """Cooldown in Sekunden"""
        if seconds < 0:
            return await ctx.send("❌ Cooldown muss ≥ 0 sein")
        await self.config.guild(ctx.guild).cooldown.set(seconds)
        await ctx.send(f"⏱ Cooldown gesetzt auf {seconds}s")

    # --- Only if empty ---
    @supportping.command()
    async def onlyifempty(self, ctx, value: bool):
        """Nur pingen wenn Channel leer war"""
        await self.config.guild(ctx.guild).only_if_empty.set(value)
        await ctx.send(f"👥 Nur wenn leer: {value}")

    # --- Status ---
    @supportping.command()
    async def status(self, ctx):
        """Zeigt aktuelle Einstellungen"""
        data = await self.config.guild(ctx.guild).all()
        vc = self.bot.get_channel(data['voice_channel'])
        tc = self.bot.get_channel(data['text_channel'])
        role = discord.utils.get(ctx.guild.roles, id=data['role']) if data['role'] else None

        await ctx.send(
            f"📊 **SupportPing Status**\n"
            f"Enabled: {data['enabled']}\n"
            f"Cooldown: {data['cooldown']}s\n"
            f"Only if empty: {data['only_if_empty']}\n"
            f"Voice Channel: {vc.mention if vc else 'Nicht gesetzt'}\n"
            f"Text Channel: {tc.mention if tc else 'Nicht gesetzt'}\n"
            f"Role: {role.mention if role else 'Nicht gesetzt'}"
        )

    # --- Version ---
    @supportping.command()
    async def version(self, ctx):
        """Zeigt die aktuelle Version des Cogs an"""
        await ctx.send(f"📦 SupportPing Version: {__version__}")
