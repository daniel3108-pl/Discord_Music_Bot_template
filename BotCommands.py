import discord
from discord.ext import commands, tasks
import asyncio
import os
import re
from MusicSource import MusicSource

class BotCommands(commands.Cog):
  """
    A class that prepares all commands for discord bot to play music in voice chat
    it extends commands.Cog class from discord API
  """

  def __init__(self, client):
    self.client = client
    self.vc = None
    self.ctx = None

    self.embed_color = 0xD93C1A

    self.queue = []
    self.current_song = None
    self.paused = False
    self.stop_from_leaving = False

    self.player_daemon.start()

  @commands.command()
  async def join(self, ctx):
    """
      A method that joins bot to voice channel that comamnd author is in currently
    """
    async with asyncio.Lock():
      if ctx.author.voice is None:
        embedVar = discord.Embed(title="Error‼️", 
                              description="You're not in a voice channel! 😢",
                              color=self.embed_color)
        await ctx.send(embed=embedVar)
        return False

      channel = ctx.author.voice.channel

      if ctx.voice_client is None:
        await channel.connect()
      else:
        await ctx.voice_client.move_to(channel)
        self.vc = ctx.voice_client
        self.ctx = ctx
      return True
  
  @commands.command()
  async def disconnect(self, ctx, message="I left your voice channel! 😢"):
    """
      A Method that disconnect bot from channel
    """
    self.queue = []
    self.current_song = None
    self.paused = False

    embedVar = discord.Embed(title="Leaving the Channel", 
                              description=message, color=self.embed_color)
    await ctx.send(embed=embedVar)
    await ctx.voice_client.disconnect()

  @commands.command(aliases=["h"])
  async def help(self, ctx):
    """
      Method that displays all available commands for this bot
    """

    Message = "Hello this is a help section!\n\
These are the commands that you can use:\n\n\
> **`$play [url/search query]`** - To play a song,\n> \n\
> **`$skip`** - to skip a song,\n> \n\
> **`$pause`** - to pause a song,\n> \n\
> **`$resume`** - to resume a song,\n> \n\
> **`$forcestop`** - to stop playing and clear queue,\n> \n\
> **`$queue`** - to show current queue,\n> \n\
> **`$join`** - to join bot to the vc,\n> \n\
> **`$disconnect`** - to disconnect bot from vc\n> \n\
> **`$clear_queue`** - to clear bot's queue\n\n"
    embedVar = discord.Embed(title="Help Section", description=Message, 
                              color=self.embed_color)  
    await ctx.send(embed=embedVar)


  @commands.command(aliases=['p'])
  async def play(self, ctx, arg, *url):
    """
      This method app new songs to the bot's queue to play it in voice chat
    """

    if len(url) == 0:
      embedVar = discord.Embed(title="Error‼️", 
                        description="Empty argument! 😢", color=self.embed_color)
      await ctx.send(embed=embedVar)
      return

    query = " ".join(url)
    self.stop_from_leaving = True
    
    musicSource = MusicSource(query, ctx.author)
    song_tuple = await musicSource.get_source_data()
    
    if song_tuple is None:
      embedVar = discord.Embed(title="Error‼️", 
                        description="Could not find any songs that\
                        matches your query! 😥", color=self.embed_color)
      await ctx.send(embed=embedVar)
      await ctx.message.add_reaction("👎")
      return
    
    if not await self.join(ctx):
      return
    self.ctx = ctx
    self.vc = ctx.voice_client

    em_title = "Playlist was Found 😀" if len(song_tuple)>1 else "Song was Found 😀"
    em_desc = f"Added song/s to the Queue! 🥳: \n"

    for t in song_tuple:
      self.queue.insert(0, t)
      em_desc += f"> **[{t[0]}]({t[3]})** | **{t[2]}** \n"

    em_desc += f"Requested by: **{song_tuple[0][4]}**\n" 

    embedVar = discord.Embed(title=em_title, 
            description=em_desc,
            color=self.embed_color)
    await ctx.send(embed=embedVar)
    
    self.stop_from_leaving = False
    await ctx.message.add_reaction("👍")

  @tasks.loop(seconds=1)
  async def player_daemon(self):
    """
      This is a task method that runs every single second and start playing next song in queue if it's not empty
    """
    try:
      if (self.vc != None and self.ctx != None and not self.vc.is_playing() and 
          len(self.queue) > 0 and not self.paused):
          url = self.queue.pop(-1)
          self.current_song = url

          embedVar = discord.Embed(title="▶️ Now Playing:", 
                                  description=f"", color=self.embed_color)
          embedVar.add_field(name="Title:", 
                        value=f"> **[{url[0]}]({url[3]})**", inline=False)
          embedVar.add_field(name=f"Duration:", 
                        value=f"> {url[2]}", inline=True)
          embedVar.add_field(name=f"Requested by:", 
                        value=f"> {url[4]}", inline=True)
          await self.ctx.send(embed=embedVar)

          source = await discord.FFmpegOpusAudio.from_probe(url[1])
          self.vc.play(source)
          
      elif (not self.stop_from_leaving and not self.vc.is_playing() and 
            len(self.queue) == 0 and self.ctx.voice_client != None 
            and not self.paused):
        await self.disconnect(self.ctx, 
                message="Queue is empty!\nSo I left the voice channel! 😥")
    except Exception as e2:
      pass

  @commands.command(aliases=['s'])
  async def skip(self, ctx):
    """
      A method that takes care of skiping current played song
    """
    self.paused = False
    ctx.voice_client.stop()

    embedVar = discord.Embed(title="", description="Skipped the Song! ⏭",
                             color=self.embed_color)
    await ctx.send(embed=embedVar)
    await ctx.message.add_reaction("👍")

  @commands.command(aliases=['fs'])
  async def forcestop(self, ctx):
    """
      This method stops playing current song, empties queue and disconnect the bot
    """

    self.paused = False
    self.queue = []
    self.current_song = None

    embedVar = discord.Embed(title="Force Stop‼️", 
                            description="Stopped playing any songs! ⏹\n\
                            Cleared the Queue and disconnected", 
                            color=self.embed_color)
    await ctx.send(embed=embedVar)

    ctx.voice_client.stop()
    await ctx.voice_client.disconnect()
    await ctx.message.add_reaction("👍")
    
  @commands.command()
  async def pause(self, ctx):
    """
      A method that stops current played song
    """
    await ctx.message.add_reaction("👍")
    self.paused = True

    embedVar = discord.Embed(title="", description="Paused the song! ⏸", 
                              color=self.embed_color)
    await ctx.send(embed=embedVar)

    await self.ctx.voice_client.pause()
    

  @commands.command(aliases=['r'])
  async def resume(self, ctx):
    """
      A method that resumes current song that was stoped
    """
    await ctx.message.add_reaction("👍")
    embedVar = discord.Embed(title="", description="Resumed the song! ▶️", 
                              color=self.embed_color)
    await ctx.send(embed=embedVar)

    await self.ctx.voice_client.resume()
    self.paused = False
    
    
  @commands.command(aliases=['q'])
  async def queue(self, ctx):
    """
      This method displayes bot's queue
    """
    i = 1
    if len(self.queue) > 0:
      Message = "\n"
      for q in self.queue[::-1]:
        Message += f"> **{i}**)   [{q[0]}]({q[3]}) | {q[2]}\n"
        i += 1
      Message += "\n"
    else:
      Message = "> Queue is Empty! ☹️"

    if self.current_song is None:
      cur_song_str = "There is no song currently playing! 😔" 
    else:
      cs = self.current_song
      cur_song_str =  f"[{cs[0]}]({cs[3]}) | {cs[2]}"

    embedVar = discord.Embed(title="Queue", description="", color=self.embed_color)
    embedVar.add_field(name="Currently Playing Song ▶️:\n", 
                        value=f"> {cur_song_str}", inline=False)
    embedVar.add_field(name=f"Still in the Queue ({len(self.queue)}):\n",
                       value=Message, inline=False)
    await ctx.send(embed=embedVar)

  @commands.command(aliases=["cq"])
  async def clear_queue(self,ctx):
    """
      This method clears bot's queue
    """
    self.queue = []
    embedVar = discord.Embed(title="Clear Queue", description="I have cleared the Queue", color=self.embed_color)  
    await ctx.send(embed=embedVar)
    await ctx.message.add_reaction("👍")

def setup(client):
  """
    This method adds command class to bot client
  """
  client.add_cog(BotCommands(client))
