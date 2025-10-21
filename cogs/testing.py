from discord.ext import commands

class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def testing(self, ctx):
        await ctx.send("Command testing executed!")

async def setup(bot):
    await bot.add_cog(Testing(bot))
