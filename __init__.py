from .supportping import SupportPing

async def setup(bot):
    await bot.add_cog(SupportPing(bot))
