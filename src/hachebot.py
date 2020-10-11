import os
from discord.ext import commands
from dotenv import load_dotenv

from HacheCog import HacheCog

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.add_cog(HacheCog(bot))

bot.run(TOKEN)
