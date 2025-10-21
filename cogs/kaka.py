from discord.ext import commands

class Kaka(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def kaka(self, ctx):
        await ctx.send("J'tes chié dessus")

async def setup(bot):
    await bot.add_cog(Kaka(bot))