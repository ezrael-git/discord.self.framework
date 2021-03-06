# deforder.py

# contains all the default orders, also called deforders
# deforders are executed directly, there is no need to worker.hear()



class Deforders:
  def __init__(self, target, **kwargs):
    # kwarg handling
    """
    Deforder constructor
    Args:
      target (discord.etc) : the channel or guild that should be targeted

    Kwargs:
      wait (list, [60-600]) : a list containing the number of seconds that should be waited for, the definite number is picked randomly each time it's used in a class method
      break_after (int, 100) : number of iterations before the loop breaks, note: only used in mass_message
      output (bool, False) : whether output generated by the class should be logged to the console or not

    Note:
      These limits are set to keep your userbot safe.
      You may override them by passing them as a keyworded-argument to the method.
    """

    # config
    if kwargs.get("passing") == True:
      kwargs = kwargs.get("pass_this")

    wait = kwargs.get("wait", list(range(60, 600)))
    break_after = kwargs.get("break_after", 100)
    output = kwargs.get("output", False)

    # self declarations
    self.target = target
    self.wait = wait
    self.break_after = int(break_after)
    self.type = type(target)
    self.output = output

  # raises a ValueError with a prefix
  def _err(self, arg):
    raise ValueError("dsf::errors::" + str(arg))

  # puts a print statement out with a prefix
  def _not(self, arg):
    print("dsf::deforders::" + str(arg))

  # pick random number from self.wait
  # another strategy used to evade API detection
  def _wait(self):
    return random.choice(self.wait)

  # mass msg a channel
  async def mass_message(self, content):
    if self.type != discord.TextChannel:
      self._err("mass_message() accepts only discord.TextChannel")
      return
    
    for i in range(self.break_after):
      await self.target.send(str(content))
      if self.output:
        self._not(f"iteration {i}")
      await asyncio.sleep(self._wait())
      # loop end ensurer
      if i == self.break_after:
        break

  # mass dm a guild's members
  async def mass_dm(self, content, **kwargs):
    if self.type != discord.Guild:
      self._err("mass_dm() accepts only discord.Guild")
      return

    # handling kwargs

    # number of members to msg (optional) (list with elements from and to), if len(list) is 0 assume all that are present in the guild
    members_limit = kwargs.get("members", [])
    # members to ignore
    ignore = kwargs.get("ignore", [])
    # network object
    network = kwargs.get("network", None)

    # figuring out what members to msg
    if len(members_limit) == 0:
      members = self.target.members
    else:
      members = self.target.members[members_limit[0]:members_limit[1]]

    # actually doing the messaging

    count = 0
    total_members = len(members)
    network_converted = []
    if network != None:
      for m in network.workers:
        network_converted.append(m.bot.user.id)
    for member in members:
      count += 1
      wait = self._wait()
      if member.bot:
        self._not(f"skipped {member.name}#{member.discriminator} because of BotUser || member {count} of {total_members}")
        continue
      if isinstance(member,discord.ClientUser):
        self._not(f"skipped {member.name}#{member.discriminator} because of ClientUser || member {count} of {total_members}")
        continue
      if member.id in network_converted:
        self._not(f"skipped {member.name}#{member.discriminator} because of NetworkUser || member {count} of {total_members}")
        continue
      if not member.id in ignore:
        try:
          await member.send(str(content))
        except Exception as e:
          self._not(f"skipped {member.name}#{member.discriminator} because of Exception: {e} || member {count} of {total_members}")
          continue
        if self.output:
          self._not(f"messaged {member.name}#{member.discriminator} || member {count} of {total_members} || next in {wait}s")
        await asyncio.sleep(wait)
      else:
        if self.output:
          self._not(f"ignored {member.name}#{member.discriminator} || member {count} of {total_members}")
        continue
