import discord
from discord.ext import commands, tasks
import os
import random
from replit import db
from keep_alive import keep_alive

keys = db.keys()

if len(keys) < 4:
  db["reaction_title"] = []
  db["reactions"] = []
  db["roles"] = [] 
  db["reaction_message_id"] = []

# Bot instance
client = commands.Bot(command_prefix='.')

reaction_title = ""
reactions = {}
reaction_message_id = ""

# On ready
@client.event
async def on_ready():
  # Bot status
  await client.change_presence(status=discord.Status.idle, activity=discord.Game('Server Management'))
  print('Bot is ready.')

@client.command()
async def clear_db(ctx):
  db["reaction_title"] = []
  db["reactions"] = []
  db["roles"] = []
  db["reaction_message_id"] = []

  await ctx.send('Database erased!')

@client.command()
async def clear(ctx, amount=2):
  await ctx.channel.purge(limit=amount)

@client.command(name="reaction_create_post")
async def reaction_create_post(ctx):
  embed = discord.Embed(title="Create Reaction Post", color=0x0455BF)
  # embed.set_author(name="Management Bot")
  embed.add_field(name="Set Title", value=".reaction_set_title \"New Title\"", inline=False)
  embed.add_field(name="Add Role", value=".reaction_add_role @Role EMOJI_HERE", inline=False)
  embed.add_field(name="Remove Role", value=".reaction_remove_role @Role", inline=False)
  embed.add_field(name="Send Creation Post", value=".reaction_send_post", inline=False)

  await ctx.send(embed=embed)
  await ctx.message.delete()


@client.command(name="reaction_set_title")
async def reaction_set_title(ctx, new_title):

  global reaction_title
  reaction_title = new_title
  # Database
  db["reaction_title"] += [new_title]
  print(db["reaction_title"])
  await ctx.send(f'The title for the message is now `{reaction_title}`!')
  await ctx.message.delete()

@client.command(name='reaction_add_role')
async def reaction_add_role(ctx, role: discord.Role, reaction):
  if role != None:
    reactions[role.name] = reaction
    await ctx.send(f"Role `{role.name}` has been added with the emoji {reaction}")
    await ctx.message.delete()
  else:
    await ctx.send("Invalid Command.")

@client.command(name='reaction_remove_role')
async def reaction_remove_role(ctx, role: discord.Role):
  if role.name in reactions:
    del reactions[role.name]
    await ctx.send(f"Role `{role.name}` has been deleted!")
    await ctx.message.delete()
  else:
    await ctx.send("Role was never added.")

@client.command(name='reaction_send_post')
async def reaction_send_post(ctx):
  global reactions
  description = "React to add the roles!\n"

  for role in reactions:
    description += f"`{role}` - {reactions[role]} \n"
    db["reactions"] += [reactions[role]]
    db["roles"] += [role]

  embed = discord.Embed(title=reaction_title, description=description)

  message = await ctx.send(embed=embed)

  global reaction_message_id
  reaction_message_id = str(message.id)
  db['reaction_message_id'] += [str(message.id)]

  for role in reactions:
    await message.add_reaction(reactions[role])
  await ctx.message.delete()

  reactions = {}

@client.event
async def on_raw_reaction_add(payload):

  for msg_id in db['reaction_message_id']:
    if str(payload.message_id) == msg_id:

      guild_id = payload.guild_id
      guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
      print(guild)

      user= await(await client.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)

      print(payload.emoji)

      if not user.bot:
        if user is not None:
          role_to_give = ""
          for role in db['roles']:
            print(db['roles'].index(role))
            if str(db['reactions'][db['roles'].index(role)]) == str(payload.emoji):
              print('MATCHING EMOJIS')
              role_to_give = role
              break

          role_for_reaction = discord.utils.get(user.guild.roles, name=role_to_give)
          await user.add_roles(role_for_reaction)

@client.event
async def on_raw_reaction_remove(payload):
  print('testing!!!!')

  for msg_id in db['reaction_message_id']:
    print(msg_id)
    if str(payload.message_id) == msg_id:

      guild_id = payload.guild_id
      guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)

      user= await(await client.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)

      print(payload.emoji)

      if not user.bot:
        if user is not None:
          role_to_remove = ""
          for role in db['roles']:
            print(db['roles'].index(role))
            if str(db['reactions'][db['roles'].index(role)]) == str(payload.emoji):
              print('MATCHING EMOJIS')
              role_to_remove = role
              break

          role_for_reaction = discord.utils.get(user.guild.roles, name=role_to_remove)
          await user.remove_roles(role_for_reaction)
        else:
            print("User not found")

keep_alive()
client.run(os.getenv('TOKEN'))