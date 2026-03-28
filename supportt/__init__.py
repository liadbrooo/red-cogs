from .supportping import SupportPing  # importiere die Klasse aus supportping.py

def setup(bot):
    """Cog laden"""
    bot.add_cog(SupportPing(bot))
