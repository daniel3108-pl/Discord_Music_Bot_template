# This is a template for Discord music bot with command support and events.
# Change a **MusicSource interface class** to add different website support
#
# Created by: Daniel Świetlik
# Github: https://github.com/daniel3108-pl
# On: 19-09-2021
#
# License: GNU General Public License v3.0

# If running not on replit uncomment this section and
# remove import discord and from discord belowe, else don't change anything

# from packageCheck import check_pakages
# if check_pakages():
#   import discord
#   from discord.ext import commands
# else: 
#   raise Exception("Could not import necessary packages")

import discord
from discord.ext import commands
from credential import TOKEN
from BotCommands import BotCommands

class BotClient:
  """
    Main bot client class that adds command class to it and runs a bot
  """
  def __init__(self, token):
    self.token = token
    self.client = commands.Bot(command_prefix="$", help_command=None)
    self.client.add_cog(BotCommands(self.client))
    self.cog_class_instance = self.client.get_cog("BotCommands")

  def run(self):
    self.events()
    self.client.run(self.token)
    
  # here in this method you can add new discord events
  # but it has to be inside it
  def events(self):
    
    @self.client.event
    async def on_command_error(ctx, error):
      print(error)
      if isinstance(error, commands.CommandNotFound):
        embedVar = discord.Embed(title="Error‼️", 
                      description=f"Unknown command - \
                      `{ctx.message.content.split()[0]}`\n\
                      Try using `$help` to show all available commands ‼️",
                                color=0xD93C1A)
        await ctx.send(embed=embedVar)
      
      
if __name__ == "__main__":
  bot = BotClient(TOKEN)
  bot.run()