import discord
from discord.ext import commands
import json
import os

# ==================== CONFIG ====================
CONFIG_FILE = 'config.json'

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {}

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# ==================== PREFIX HANDLER ====================
def get_prefix(bot, message):
    if message.guild is None:
        return '!'
    gid = str(message.guild.id)
    return config.get(gid, {}).get('prefix', '!')

# ==================== INTENTS & BOT ====================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# ==================== HELPER: SEND LOG TO BOTH CHANNELS ====================
async def send_log(guild: discord.Guild, embed: discord.Embed):
    gid = str(guild.id)
    data = config.get(gid, {})

    # Public log
    if data.get('public_log'):
        channel = guild.get_channel(data['public_log'])
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass

    # Private log
    if data.get('private_log'):
        channel = guild.get_channel(data['private_log'])
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass

# ==================== EVENTS (unchanged - logs everything except messages) ====================
@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    print('Use /logsettings or !logsettings to check configuration')
    
    # SYNC HYBRID COMMANDS (slash commands appear instantly)
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} hybrid commands globally')
    except Exception as e:
        print(f'⚠️ Sync failed: {e}')

# (All your on_member_join, on_member_remove, on_voice_state_update, etc. stay EXACTLY the same as before)

# ==================== HYBRID COMMANDS ====================

# Change prefix per server
@bot.hybrid_command(name="setprefix", description="Change the bot prefix for this server")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    if len(new_prefix) > 10 or len(new_prefix) < 1:
        await ctx.send("❌ Prefix must be 1-10 characters.")
        return
    gid = str(ctx.guild.id)
    if gid not in config:
        config[gid] = {}
    config[gid]['prefix'] = new_prefix
    save_config()
    await ctx.send(f"✅ Prefix changed to `{new_prefix}`\nYou can now use `/{ctx.command.name}` or `{new_prefix}{ctx.command.name}`")

# Set Public Log Channel
@bot.hybrid_command(name="setpubliclog", description="Set the public log channel (visible to everyone)")
@commands.has_permissions(administrator=True)
async def setpubliclog(ctx, channel: discord.TextChannel):
    gid = str(ctx.guild.id)
    if gid not in config:
        config[gid] = {}
    config[gid]['public_log'] = channel.id
    save_config()

    everyone = ctx.guild.default_role
    await channel.set_permissions(everyone, view_channel=True)

    await ctx.send(f"✅ **Public Logs** set to {channel.mention}\nEveryone can see these logs.")

# Set Private Log Channel + Auto Lock
@bot.hybrid_command(name="setprivatelog", description="Set the private log channel (auto-locks for @everyone)")
@commands.has_permissions(administrator=True)
async def setprivatelog(ctx, channel: discord.TextChannel):
    gid = str(ctx.guild.id)
    if gid not in config:
        config[gid] = {}
    config[gid]['private_log'] = channel.id
    save_config()

    everyone = ctx.guild.default_role
    await channel.set_permissions(everyone, view_channel=False)

    whitelists = config[gid].get('whitelist_roles', [])
    for rid in whitelists:
        role = ctx.guild.get_role(rid)
        if role:
            await channel.set_permissions(role, view_channel=True, read_message_history=True)

    await ctx.send(f"✅ **Private Logs** set to {channel.mention}\n"
                   f"Channel is now **locked** for @everyone.\n"
                   f"Use `/addwhitelistrole` to give access to staff roles.")

# Add Whitelist Role
@bot.hybrid_command(name="addwhitelistrole", description="Add a role that can see private logs")
@commands.has_permissions(administrator=True)
async def addwhitelistrole(ctx, role: discord.Role):
    gid = str(ctx.guild.id)
    if gid not in config:
        config[gid] = {}
    if 'whitelist_roles' not in config[gid]:
        config[gid]['whitelist_roles'] = []
    if role.id not in config[gid]['whitelist_roles']:
        config[gid]['whitelist_roles'].append(role.id)
        save_config()

        if config[gid].get('private_log'):
            ch = ctx.guild.get_channel(config[gid]['private_log'])
            if ch:
                await ch.set_permissions(role, view_channel=True, read_message_history=True)

        await ctx.send(f"✅ {role.mention} can now see **Private Logs**.")
    else:
        await ctx.send("❌ Role already whitelisted.")

# Remove Whitelist Role
@bot.hybrid_command(name="removewhitelistrole", description="Remove a role from private log whitelist")
@commands.has_permissions(administrator=True)
async def removewhitelistrole(ctx, role: discord.Role):
    gid = str(ctx.guild.id)
    data = config.get(gid, {})
    if 'whitelist_roles' in data and role.id in data['whitelist_roles']:
        data['whitelist_roles'].remove(role.id)
        save_config()

        if data.get('private_log'):
            ch = ctx.guild.get_channel(data['private_log'])
            if ch:
                await ch.set_permissions(role, view_channel=None)

        await ctx.send(f"✅ {role.mention} removed from private log whitelist.")
    else:
        await ctx.send("❌ Role was not whitelisted.")

# List Whitelist Roles
@bot.hybrid_command(name="whitelistroles", description="List all roles that can see private logs")
@commands.has_permissions(administrator=True)
async def whitelistroles(ctx):
    gid = str(ctx.guild.id)
    roles = config.get(gid, {}).get('whitelist_roles', [])
    if not roles:
        await ctx.send("No whitelisted roles yet.")
        return
    role_list = [ctx.guild.get_role(rid).mention for rid in roles if ctx.guild.get_role(rid)]
    await ctx.send(f"**Private Log Whitelist:**\n" + "\n".join(role_list))

# View All Settings
@bot.hybrid_command(name="logsettings", description="Show current logging configuration")
@commands.has_permissions(administrator=True)
async def logsettings(ctx):
    gid = str(ctx.guild.id)
    data = config.get(gid, {})
    public_ch = ctx.guild.get_channel(data.get('public_log'))
    private_ch = ctx.guild.get_channel(data.get('private_log'))
    prefix = data.get('prefix', '!')

    embed = discord.Embed(title="📋 Logging Settings", color=discord.Color.blurple())
    embed.add_field(name="Prefix", value=f"`{prefix}`", inline=False)
    embed.add_field(name="Public Log Channel", value=public_ch.mention if public_ch else "Not set", inline=False)
    embed.add_field(name="Private Log Channel", value=private_ch.mention if private_ch else "Not set", inline=False)
    wl = [ctx.guild.get_role(rid).mention for rid in data.get('whitelist_roles', []) if ctx.guild.get_role(rid)]
    embed.add_field(name="Private Whitelist Roles", value="\n".join(wl) if wl else "None", inline=False)
    await ctx.send(embed=embed)

# ==================== RUN BOT ====================
if __name__ == "__main__":
    bot.run("YOUR_BOT_TOKEN_HERE")  # ← Replace with your token
