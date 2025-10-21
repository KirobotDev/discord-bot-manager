from discord.ext import commands

class Ntm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ntm(self, ctx):
        await ctx.send("Command ntm executed!")

async def setup(bot):
    await bot.add_cog(Ntm(bot))