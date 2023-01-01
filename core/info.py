import asyncio
import datetime
import os
import platform
import random
import threading
import time

import aiohttp
import discord
import psutil
from discord.ext import commands


async def local58(ctx):
    possible = [
        [ # 1 Contingency
            "**U.S DEPARTMENT FOR THE PRESERVATION OF AMERICAN DIGNITY**",
            "Contingecy message will now begin. Please comply with the following instructions. God bless America.",
            "\n"
            "The worst has come to pass."
            "Despite the sacrifices of our citizens and the might of our armed forced, the UNITED STATES has been forced to surrender to her enemy."
            "Though they may occupy our borders, our streets and our homes... the enemy will never occupy our SPIRIT."
            "\n"
            "\n"
            "YOU TAKE AMERICA WITH YOU."
            "THE 51ST STATE IS NOT A PLACE."
        ].join("\n"),
        [ # 2 Weather Service
            "**WEATHER WARNING**",
            "The County Weather Service has issued a warning for a meteorological event.",
            "\n"
            "This warning is effective immediately and continues until sunrise tomorrow morning.",
            "Citizens are advised not to observe this event with the naked eye.",
            "**CIVIL DANGER ALERT**",
            "For your saftey, remain indoors. Do not look at the night sky.\nMore information to follow.",
            "\n\nTHE METEOROLOGICAL EVENT IS SAFE FOR ALL TO VIEW. WARNING HAS BEEN LIFTED.\n"
            "GO OUTSIDE NOW."
        ].join("\n"),
        [ # 3 A Look Back
            "We send signals to ourselves"
            "Thru their domain"
            "Did we really believe"
            "They wouldn't add our own?"
            "\n"
            "Don't touch that dial. More to come."
            "**We begin our broadcast day.**"
        ].join("\n"),
        [ # 4 Digital Transition
            "UNTHINKING THEY MOVE."
            "TO CUT HIS THROAT"
            "ONLY TO MAKE"
            "A THOUSAND MOUTHS"
            "IF HE IS SILENCED"
            "WE WILL SPEAK FOR HIM"
            "SIGNS AND WONDERS"
            "FLOOD OUR LITTLE SKY"
            "NO STARS ABOVE"
            "ONLY EYES"
            "WAITING TO OPEN"
        ].join("\n"),
        # 5 Merch
            "**Civil Danger Warning**\n"
            "DO NOT LOOK AT THE MOON.\n"
            "AVOID MIRRORS.\n"
            "STAY INDOORS.\n"
            "DO NOT BE AFRAID.\n"
            "\n"
            "ACT IMMEDIATELY.\n"
            "GO OUTSIDE NOW.\n"
            "ITS IN THE LIGHT.",
    ]
    
    # Generate the embed #
    em = discord.Embed(description=random.choice(possible),
                       color=0x04024a)
    em.set_footer(text="This concludes our broadcast day. Good night.")
    em.set_author(name="Local58 WCLV-TV", icon_url="https://media.discordapp.net/attachments/1030143502912344114/1030143541286023289/local58.jpg")
    msg = await ctx.send(embed=em)
    await asyncio.sleep(5)
    await msg.delete()
    # Award the user with the Local58 badge #
    badges = ctx.bot.db.users.find_one({"id": ctx.author.id})["badges"]
    # If the user already has the badge, do nothing #
    if "local58" not in badges:
        badges.append("local58")
        ctx.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"badges": badges}})
        await ctx.author.send("You have been awarded the **Broadcast Concluded** badge.\nJust hope you stay in the light.")
    
    
    # Then reinvoke the command #
    await ctx.invoke(ctx.command)

async def resonate2(ctx):
    # Start the teaser #
    em = discord.Embed(title="After 6 long months...")
    msg = await ctx.send(embed=em)
    await asyncio.sleep(2)
    # Join the VC #
    vc = await ctx.author.voice.channel.connect()
    em.description = "Several mental breakdowns, two-hundred hot chocolate packets, and eight thousand swears later..."
    await msg.edit(embed=em)
    await asyncio.sleep(2)
    # Start the audio track # 
    vc.play(discord.FFmpegPCMAudio(source="./assets/WhereIsYourSaviour.mp3",executable="./assets/ffmpeg.exe"))
    await asyncio.sleep(1)
    em.title = "We are proud to present..."
    em.description = None
    await msg.edit(embed=em)
    await asyncio.sleep(14) # Wait for the audio to reach 15 seconds in #

    while vc.is_playing():
        em.title = "Frostbyte: Arctic Sunrise"
        em.description = "A rewritten protogen, with a new look, new features, and a new attitude."
        await msg.edit(embed=em)
        await asyncio.sleep(5)
        em.description = "Written in pure Python, with <3 by Robyn (and several others)."
        await msg.edit(embed=em)
        await asyncio.sleep(3)
        em.description = "Credits to the following people:"
        await msg.edit(embed=em)
        await asyncio.sleep(2)
        # Credits #
        # Robyn #
        usr = ctx.bot.get_user(478675118332051466)
        em.add_field(name=usr.name, value="Lead Developer, Lead Designer, Lead Tester, Lead Supporter, Lead Everything", inline=False)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        # Leaf #
        usr = ctx.bot.get_user(659488296820408355)
        em.add_field(name=usr.name, value="Website and bot helper, Dutch translator.", inline=False)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        # Luna #
        usr = ctx.bot.get_user(376406094639267862)
        em.add_field(name=usr.name, value="Original Frostbyte lead developer, German translator", inline=False)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        # Cipher #
        usr = ctx.bot.get_user(291616164574920704)
        em.add_field(name=usr.name, value="Original Frostbyte website dashboard backend helper", inline=False)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        # Zinc #
        usr = ctx.bot.get_user(531460025370017803)
        em.add_field(name=usr.name, value="Spanish translator.", inline=False)
        await msg.edit(embed=em)
        await asyncio.sleep(15)
        # Clear the embed #
        em.clear_fields()
        em.title = "Frostbyte: Arctic Sunrise"
        em.description = "Coming soon to a Discord server near you."
        await msg.edit(embed=em)
        await asyncio.sleep(10) # Loop around until the audio finishes #
    await vc.disconnect()
    await msg.delete()
    
    # Award the user with the Resonate badge #
    badges = ctx.bot.db.users.find_one({"id": ctx.author.id})["badges"]
    # If the user already has the badge, do nothing #
    if "resonate" not in badges:
        badges.append("resonate")
        ctx.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"badges": badges}})
        await ctx.author.send("You have been awarded the **Resonate** badge.\nThat was a pretty good intro, if I do say so myself.")
    

class Informational(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief="Shows the bot's stats.")
    async def stats(self, ctx):
        available_ram = psutil._common.bytes2human(psutil.virtual_memory().available)
        used_ram = psutil._common.bytes2human(psutil.virtual_memory().used)
        cpu = psutil.cpu_percent()
        total_ram = psutil._common.bytes2human(psutil.virtual_memory().total)
        
        # Bot uptime (in human readable) #
        time_since = round(time.time() - self.bot.started_at) 
        min_since = round(time_since / 60) 
        hour_since = round(min_since / 60) 
        day_since = round(hour_since / 24)
        
        time_since = time_since % 60
        min_since = min_since % 60
        hour_since = hour_since % 24

        # em = discord.Embed(title="Bot Stats", color=self.bot.main_color())
        # em.add_field(name="Ping", value=f"{round(self.bot.latency * 1000,2)}ms")
        # em.add_field(name="Uptime", value=f"{day_since} days, {hour_since} hours, {min_since} minutes, {time_since} seconds")
        # em.add_field(name="System Usage", value=f"Memory: {used_ram}B / {total_ram}B ({available_ram}B available)\nCPU: {cpu}%")
        # em.add_field(name="Network Usage", value=f"Download: {psutil._common.bytes2human(psutil.net_io_counters().bytes_recv)}B\nUpload: {psutil._common.bytes2human(psutil.net_io_counters().bytes_sent)}B")
        # em.add_field(name="Servers", value=len(self.bot.guilds))
        # em.add_field(name="Shards", value=self.bot.shard_count)
        # em.add_field(name="Cogs", value=len(self.bot.cogs))
        # em.add_field(name="Commands", value=len(self.bot.commands))
        # em.add_field(name="Threads", value=threading.active_count())
        # em.add_field(name="Deployed", value=self.bot.deployed)
        # em.add_field(name="Version", value=self.bot.version)
        # em.add_field(name="Python Version", value=platform.python_version())
        # em.add_field(name="Discord.py Version", value=discord.__version__)
        
        # Use localised strings #
        em = discord.Embed(title=await ctx.get_locale(message="StatsTitle"), color=self.bot.main_color())
        em.add_field(name=await ctx.get_locale(message="StatsPingTitle"), value=f"{round(self.bot.latency * 1000,2)}ms"),
        em.add_field(name=await ctx.get_locale(message="StatsUptimeTitle"), value=await ctx.get_locale(message="StatsUptimeDescription",days=day_since,hours=hour_since,minutes=min_since,seconds=time_since))
        em.add_field(name=await ctx.get_locale(message="StatsSystemUsageTitle"), value=await ctx.get_locale(message="StatsSystemUsageDescription",used=used_ram,total=total_ram,available=available_ram,cpu=cpu,threads=threading.active_count()))
        em.add_field(name=await ctx.get_locale(message="StatsNetworkUsageTitle"), value=await ctx.get_locale(message="StatsNetworkUsageDescription",download=psutil._common.bytes2human(psutil.net_io_counters().bytes_recv),upload=psutil._common.bytes2human(psutil.net_io_counters().bytes_sent)))
        em.add_field(name=await ctx.get_locale(message="StatsServersTitle"), value=len(self.bot.guilds))
        em.add_field(name=await ctx.get_locale(message="StatsShardsTitle"), value=self.bot.shard_count)
        em.add_field(name=await ctx.get_locale(message="StatsCogsTitle"), value=len(self.bot.cogs))
        em.add_field(name=await ctx.get_locale(message="StatsCommandsTitle"), value=len(self.bot.commands))
        em.add_field(name=await ctx.get_locale(message="StatsDeployedTitle"), value=self.bot.deployed)
        em.add_field(name=await ctx.get_locale(message="StatsVersionTitle"), value=self.bot.version)
        em.add_field(name=await ctx.get_locale(message="StatsLibraryTitle"), value=await ctx.get_locale(message="StatsLibraryDescription",python=platform.python_version(),discord=discord.__version__))
        
        await ctx.send(embed=em)

    @commands.command(brief="Shows a list of commands.")
    async def help(self, ctx, *, command=None):
        # 1 in 1000 chance of showing a Local58 easter egg #
        # Add it in a thread so it doesn't halt the entire bot #
        if random.randint(0, 1000) == 1:
        #if True: # For testing purposes #
            asyncio.get_event_loop().create_task(local58(ctx))
            return
            
        em = discord.Embed(title=await ctx.get_locale(message="HelpTitle"), description=await ctx.get_locale(message="HelpDescription"), color=self.bot.main_color())
        em.set_thumbnail(url=self.bot.user.avatar)
        em.set_footer(text=await ctx.get_locale(message="HelpFooter"))
        
        if command is None:   
            # Add all commands to the embed #
            for cog in sorted(self.bot.cogs):
                if cog.lower() == "admintools" and not (ctx.author.id in self.bot.owner_ids): # Don't show admin commands to non-owners # We don't use the is_owner() check as it always returns True here #
                    continue
                if cog.lower() == "nsfw" and not ctx.channel.is_nsfw(): # Don't show NSFW commands in non-NSFW channels #
                    continue
                cog_commands = self.bot.get_cog(cog).get_commands()
                cog_commands = [command for command in cog_commands if not command.hidden and command.enabled]
                
                # Sort commands alphabetically #
                cog_commands = sorted(cog_commands, key=lambda x: x.name)
                        
                if len(cog_commands) > 0:
                    cog_commands = [f"`{command.name}`" for command in cog_commands]
                    em.add_field(name=cog, value=" | ".join(cog_commands), inline=False)
        else:
            # If the command is specified, show the help for that command #
            command = self.bot.get_command(command)
            if command is None:
                await ctx.send_locale(message="HelpCommandNotFound")
                return
            if command.hidden or not command.enabled:
                await ctx.send_locale(message="HelpCommandUnavailable")
                return
            em.title = command.name
            em.description = command.help or command.brief or await ctx.get_locale(message="HelpNoDescription")
            em.add_field(name=await ctx.get_locale(message="HelpCommandUsageTitle"), value=f"``{command.name} {command.signature}``")
            if len(command.aliases) > 0:
                em.add_field(name=await ctx.get_locale(message="HelpCommandAliasesTitle"), value=" | ".join([f"`{alias}`" for alias in command.aliases])) 
            if len(command.checks) > 0:
                em.add_field(name=await ctx.get_locale(message="HelpCommandChecksTitle"), value="\n".join([f"`{check.__qualname__}`" for check in command.checks]))
            # List all subcommands #
            if isinstance(command, commands.Group):
                subcommands = command.commands
                subcommands = [command for command in subcommands if not command.hidden and command.enabled]
                if len(subcommands) > 0:
                    subcommands = [f"`{command.name}`" for command in subcommands]
                    em.add_field(name=await ctx.get_locale(message="HelpCommandSubcommandsTitle"), value=" | ".join(subcommands), inline=False)

        await ctx.reply(embed=em)
        
    @commands.command(name="ping", brief="Pong!")
    async def ping(self, ctx):
        #await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')
        msg_ping = time.time()
        msg = await ctx.send_locale(message="PingMessage")
        msg_ping = str(round((time.time() - msg_ping) * 100, 2)) + "ms"
        
        edit_ping = time.time()
        await msg.edit(content=await ctx.get_locale(message="PingEditMessage"))
        edit_ping = str(round((time.time() - edit_ping) * 100, 2)) + "ms"
        
        db_ping = time.time()
        self.bot.db.servers.find_one({"id": ctx.guild.id})
        db_ping = str(round((time.time() - db_ping) * 100, 2)) + "ms"
        
        #em = discord.Embed(title=await ctx.get_locale(message="PingFinalMessageTitle"), description=f"**Heartbeat:** {round(bot.latency * 1000,2)}ms\n**Message:** {msg_ping}\n**Edit:** {edit_ping}\n**Database:** {db_ping}", 
        em = discord.Embed(title=await ctx.get_locale(message="PingFinalMessageTitle"), description=await ctx.get_locale(message="PingFinalMessageDescription", heartbeat=f"{round(self.bot.latency * 1000,2)}ms" ,msg=msg_ping, edit=edit_ping, db=db_ping),
                        color=self.bot.main_color())
        await msg.edit(content=None, embed=em)
    
    @commands.command(name="invite", brief="Invite me to your server!")
    async def invite(self, ctx):
        #https://discord.com/api/oauth2/authorize?client_id=750114971588755477&permissions=515600936550&scope=bot
        em = discord.Embed(title=await ctx.get_locale(message="InviteMessage"),color=self.bot.main_color())
        em.add_field(name=await ctx.get_locale(message="InviteMessageTitle"), value=await ctx.get_locale(message="ClickHere",link=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=515600936550&scope=bot"))
        em.add_field(name=await ctx.get_locale(message="InviteSupportMessage"), value=await ctx.get_locale(message="ClickHere",link=f"https://discord.gg/Mqcgca8"))
        em.add_field(name=await ctx.get_locale(message="InviteSupportDeveloperMessage"), value=await ctx.get_locale(message="ClickHere",link=f"https://patreon.com/robynsnest"))
        await ctx.send(embed=em)
        
    # Not to be confused with the cog name :upside_down: #
    @commands.command(name="info", brief="Shows information about the bot")
    async def info(self, ctx):
        # Check if the user is in a voice channel #
        # Then if the date is within 10 days of the enviroment variable, trigger this #
        # If the user already has the badge, don't trigger the event at all #
        # If the easter egg is ongoing, fail silently #
        if ctx.author.voice is not None and not ctx.guild.me.voice:
            if (datetime.datetime.utcnow() - datetime.datetime.strptime(os.getenv("ARCTIC_SUNRISE_RELAUNCH"), "%Y-%m-%d")).days <= 10:
                if not "resonate" in self.bot.db.users.find_one({"id": ctx.author.id})["badges"]:
                    asyncio.get_event_loop().create_task(resonate2(ctx))
                    return

        
        em = discord.Embed(title=await ctx.get_locale(message="InfoTitle"),description=await ctx.get_locale(message="InfoDescription"),color=self.bot.main_color())
        await ctx.send(embed=em)
            
async def setup(bot):
    bot.remove_command("help")
    await bot.add_cog(Informational(bot))
