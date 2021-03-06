""" network.py
for the bundling of the manager and worker components
"""
import time

class Network:
  def __init__(self, manager: list, workers: list):
    self.manager = manager[0]
    self.workers = workers
    self.head = self.manager.bot
    self.team = [self.manager]
    for i in self.workers: self.team.append(i)

  def _bots(self):
    temp = []
    for i in self.team: temp.append(i.bot)
    return temp

  def _sendable(self, clientuser):
    return self.head.get_user(clientuser.id)

  async def _thread(self, loop):
    loop.run_forever()

  def connect(self, tokens: list, **kwargs):
    output = kwargs.get("output", False)
    wait = kwargs.get("wait", 5)
    additional = kwargs.get("additional", {})

    if output == True: print(f"Network.connect(): initiated")

    loop = asyncio.get_event_loop()
    for member,token in zip(self.team,tokens):
      loop.create_task(member.bot.start(token))
      if output == True: print(f"Network.connect(): {member} has been added to the loop")
      time.sleep(wait)

    # resolving additional
    if len(additional) != 0:
      count = 0
      for add in additional.items():
        count += 1
        _bot, _token = add[0], add[1]

        loop.create_task(_bot.start(str(_token)))
        if output == True: print(f"Network.connect(): resolved add {count} of {len(additional)}")
      time.sleep(wait)

    if output == True: print(f"Network.connect(): resolved")
    loop.run_forever()


  def disconnect(self, **kwargs):
    manager = kwargs.get("manager", False)
    for member in self.team:
      if member == self.manager:
        if manager == True:
          self.head.logout()
      else:
        member.bot.logout()
    return True
    

  async def wait_until_ready(self):
    for member in self.team:
      await member.bot.wait_until_ready()
    return True

  async def join_guild(self, invite, **kwargs):
    wait = kwargs.get("wait", 60)
    for member in self.team:
      try:
        await member.bot.join_guild(invite)
        await asyncio.sleep(wait)
      except:
        continue
    return True

  async def leave_guild(self, id, **kwargs):
    wait = kwargs.get("wait", 60)
    for member in self.team:
      try:
        await member.bot.leave_guild(id)
        await asyncio.sleep(wait)
      except:
        continue
    return True

  async def listen_for(self, type):
    if type == "command":
      for member in self.workers:
        await member.hear()

  async def send(self, channel, msg, **kwargs):
    manager = kwargs.get("manager", False)
    wait = kwargs.get("wait", 3)

    channel = int(channel)
    if manager:
      await self.head.get_channel(channel).send(msg)
    for worker in self.workers:
      try:
        await worker.bot.get_channel(channel).send(msg)
        if wait != 0:
          await asyncio.sleep(wait)
      except Exception as e:
        print(f"Error in Network.send(): {e}")

  async def dm(self, user, msg):
    for worker in self.workers:
      await worker.bot.get_user(int(user)).send(str(msg))


  def guilds(self):
    temp = []
    for member in self.team:
      for guild in member.bot.guilds:
        if not guild in temp:
          temp.append(guild)
    return temp

  # Acts of violence

  async def mass_dm(self, target, **kwargs):

    # to pass to deforders constructor
    wait = kwargs.get("wait", list(range(60,600)))
    break_after = kwargs.get("break_after", 100)
    output = kwargs.get("output", False)
    nwork = kwargs.get("network", self)
    
    # to pass to mass_dm
    members, ignore = kwargs.get("members", []), kwargs.get("ignore", [])
    content = kwargs.get("content")

    # custom
    invites = kwargs.get("invites", []) # actually just a list of invites, for when you want each worker to join a different guild and then spam
    inv = True if len(invites) != 0 else False

    
    for worker in self.workers:
      if inv == False: # default
        use = Deforders(worker.bot.get_guild(int(target)), wait=wait, break_after=break_after, output=output, network=nwork)
        await use.mass_dm(content, members=members, ignore=ignore)
      else: # special
        ind = self.workers.index(worker)
        guild = await worker.bot.join_guild(invites[ind])
        use = Deforders(guild, wait=wait, break_after=break_after, output=output, network=nwork)
        await use.mass_dm(content, members=members, ignore=ignore)


