# Where it begins. #
# The following launch parameters can be used. However, they would've been automatically set by the launcher.
# --production: Launches the bot in production mode.
# --staging: Launches the bot in staging mode.
# --pre: Launches the bot in pre-release mode.
# --debug: Launches the bot in debug mode. Provides more verbal output, however, can not be used if production is enabled, as irreversible changes can be made.
# --no-database: Disables the database. This simulates a database outage.
# --no-api: Disables all external API calls. This simulates a full internet outage. 
# --gui: Launches the bot in GUI mode. Provides real-time stats, charts, etc. This is only available on Windows.
# --suppress-events: Suppresses all events. This is NOT RECOMMENDED as this suppresses the error handler.
# --force: Forces the bot to launch. This is highly unrecommended as this can cause MAJOR unstability.
# --disallow-admin: Disallows the bot from running commands with the ``is_owner()`` check. Provides extra security however means that the bot can not run easy debug commands.
# 
# You shouldn't REALLY need to run this manually, as the launcher will do it for you. However, if you want to, you can.

import asyncio
import datetime
import difflib
import json
import logging
import os
import random
import string
import time
import traceback
import sys
import platform
import psutil

import aiohttp
import discord
import pymongo
import termcolor
from ascii_magic import Modes, from_image_file, to_terminal
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from dotenv import load_dotenv

# Import ./utils
from utils import image_generation
from utils import cdn

load_dotenv()
intents = discord.Intents.all()
intents.members = True
intents.messages = True
intents.presences = False

db = pymongo.MongoClient(os.getenv("MONGO"))

def debug_print(text):
    if "--debug" in sys.argv:
        termcolor.cprint(text, "cyan", "on_white")

async def get_prefix(bot, message=None):
    if message is None:
        if os.getenv("DEPLOYMENT").lower() == "production":
            return "fb."
        elif os.getenv("DEPLOYMENT").lower() == "staging":
            return "fbb."
        else:
            return "fba."
    try:
        if not message.guild:
            return (commands.when_mentioned_or(os.getenv("PREFIX")))(bot, message)
        else:
            return (commands.when_mentioned_or(bot.db.servers.find_one({"id": message.guild.id})["prefix"]))(bot, message)
    except:
        return (commands.when_mentioned_or(os.getenv("PREFIX")))(bot, message)

db_template = {
    "id": 0,
    "prefix": "fb.",
    "locale": "en_GB",
    "nsfwFilter": {
        "enabled": False,
        "severity": 0.45
    },
    "autoResponse": {
        "enabled": False,
        "responses": [
            # So, custom responses can come in two forms.
            # Trigger can be either a string or a list of strings. If it's a list, it will be treated as an OR statement.
            # Response can be either a string or a list of strings. If it's a list, it will be given a random choice.
            # However, both will support variables. These are:
            # {user} - The user who sent the message.
            # {server} - The server the message was sent in.
            # {channel} - The channel the message was sent in.
            # {message} - The message that was sent.
            # {prefix} - The prefix of the server.
            
            # These are the default responses. You can add more if you want.
            # Servers can also add their own responses.
            {"trigger": "pats frostbyte", "response": "^w^"},
            {"trigger": "hugs frostbyte", "response": "^w^"},
            {"trigger": "kisses frostbyte", "response": "^//w//^"},
            {"trigger": ["slaps frostbyte","punches frostbyte"], "response": ["Ow! Stop that!", "Ow! That hurt!", "Ow! Stop it!", "Ow! That's not nice!", "Ow! Stop!"]},
            {"trigger": "bad frostbyte", "response": "No, I'm a good girl!"}, # This is gonna cause multiple images to appear on R34 and e621. I'm sorry. (I'm not sorry.)
        ]
    },
    "banSync": {
        "enabled": False
    },
    "antiHoist": {
        "enabled": False
    },
    "antiInvite": {
        "enabled": False
    },
    "raidMode": {
        "enabled": False,
        "detection": {
            "severity": 0.45,
            "enabled": False
        },
        "forces": {
            "kickNewMembers": False,
            "kickRecentMembers": False,
            "lockdown": False
        }
    },
    "welcome": {
        "channel": None,
        "enabled": False,
        "customisation": {
            "image": None,
            "text": None,
        },
    },
    "leave": {
        "channel": None,
        "enabled": None,
        "customisation": {
            "image": None,
            "text": None,
        }
    },
    "antiCapsSpam": {
        "enabled": False,
        "maxAllowed": 5
    }
}

async def status_task():
    while True:
        status = random.choice([
            "a skunk in the wild 🦨",
            "a coffee machine ☕",
            "a fox with it's tail on fire 🔥",
            "birds 🐦",
            "the dogs 🐕",
            "a cat 🐈",
            "toasters 🍞",
            f"{len(bot.guilds)} servers 🌐",
            f"{len(bot.users)} users 🧑",
            f"{len(bot.support_server.members)} members in the support server! 🧑",
            "the microwave beep 🍲",
            "toasters toasting toast 🍞",
            "screaming developers 🖥️",
            "more cats 🐈",
            "the coffee machine to make coffee ☕",
            "the internet machine 🌐"
        ])
        # Set the status to the random status
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        await asyncio.sleep(30)

async def database_integrity_checker():
    while True:
        try:
            # First, check if the server is in the database
            for guild in bot.guilds:
                if bot.db.servers.find_one({"id": guild.id}) is None:
                    template = db_template
                    template["id"] = guild.id
                    bot.db.servers.insert_one({"id": guild.id, **template})
                    await bot.bot_log.send(embed=discord.Embed(title="Database Integrity Check", description=f"{guild.name} failed integrity check.\nReason: Missing config entry\nFix: Added config entry by database.", color=discord.Color.green()))
                try:
                    # Now, check if the server has all the keys
                    for key in db_template:
                        if key not in bot.db.servers.find_one({"id": guild.id}):
                            bot.db.servers.update_one({"id": guild.id}, {"$set": {key: db_template[key]}})
                            await bot.bot_log.send(embed=discord.Embed(title="Database Integrity Check", description=f"{guild.name} failed integrity check.\nReason: Missing key ``{key}``\nFix: Added key to database.", color=discord.Color.green()))
                except Exception as e: pass # This is here because if the server is missing, it will throw an error.
            
            # Finally, check if the server still has the bot. If not, remove it from the database. This is required because GPDR compliance.
            for server in bot.db.servers.find():
                if bot.get_guild(server["id"]) is None:
                    bot.db.servers.delete_one({"id": server["id"]})
                    await bot.bot_log.send(embed=discord.Embed(title="Database Integrity Check", description=f"{server['id']} failed integrity check.\nReason: Server no longer exists\nFix: Removed server from database.", color=discord.Color.green()))
            bot.database_active = True
        except Exception as e:
            # If there was an outage already, don't send another message
            if bot.database_active == False:
                pass
            # If there's an error, treat it as a database outage.
            bot.database_active = False
            
            # Get the traceback
            tb = traceback.format_exc()
            
            # Get the time
            now = datetime.datetime.now()
            now = now.strftime("%d/%m/%Y %H:%M:%S")
            
            # Output the traceback to a file to upload to the log channel
            with open("traceback.txt", "w") as f:
                f.write(tb)
                
            # Alert the bot log
            await bot.bot_log.send(content="@everyone", embed=discord.Embed(title="Database Outage Reported", description=f"**Time:** {now}\n**Error:** {e}\n\nThe bot will now use the offsite database. Offsite's data was last backed up: None", color=discord.Color.red()).set_footer(text="Traceback attached."), file=discord.File("traceback.txt"))
            
            # Delete the traceback file
            os.remove("traceback.txt")
            
        await asyncio.sleep(300) # 5 minutes

async def database_backup():
    # Backup the latest data to the offsite mongo database
    db_backup = pymongo.MongoClient(os.getenv("MONGO_OFFSITE"))
    db_backup.servers.drop()
    db_backup.users.drop()
    for server in bot.db.servers.find():
        db_backup.servers.insert_one(server)
    for user in bot.db.users.find():
        db_backup.users.insert_one(user)
    db_backup.close()
    
    with open("./data/backup.json", "w") as f:
        json.dump({"last_backup": time.time(), "guildsBacked": len(bot.db.servers.find()), "usersBacked": len(bot.db.users.find())}, f)
        
    await bot.bot_log.send(embed=discord.Embed(title="Database Backup", description=f"Backed up {len(bot.db.servers.find())} servers and {len(bot.db.users.find())} users to the offsite database.", color=discord.Color.green()))
    await asyncio.sleep(43200) # 12 hours

# Add custom context commands #
# Mostly for localization #
class CustomContext(commands.Context):
    async def get_used_locale(self):
        """Get the locale that the server or user is using."""
        try: # Whoever invented the KeyError exception to run in or statements I wish you a slow and painful death
            locale = (self.bot.db.users.find_one({"id": self.author.id}).get("language") or self.bot.db.servers.find_one({"id": self.guild.id}).get("locale")) or "en_GB" # If there is no user locale, use the server locale. If there is no server locale, use en_GB
        # If theres either a TypeError or AttributeError, check if the server has a locale. If not, use en_GB
        except TypeError: 
            try:
                locale = self.bot.db.servers.find_one({"id": self.guild.id})["locale"] or "en_GB"
            except TypeError:
                locale = "en_GB"
            except KeyError:
                locale = "en_GB"
            except Exception as e: raise e
        except AttributeError: 
            try:
                locale = self.bot.db.servers.find_one({"id": self.guild.id})["locale"] or "en_GB"
            except TypeError:
                locale = "en_GB"
            except KeyError:
                locale = "en_GB"
            except Exception as e: raise e
        except KeyError:
            locale = "en_GB"
        except Exception as e: raise e
        
        return locale
    
    async def send_locale(self, **kwargs):
        """Sends a message from the locale file"""
        # Send the message #
        #return await self.reply(await self.get_locale(**kwargs))
        # Embed the message, before sending #
        em = discord.Embed(description=await self.get_locale(**kwargs), color=bot.main_color())
        return await self.reply(embed=em)
    
    async def get_locale(self, **kwargs):
        """Gets a message from the locale file"""
        # Get the server's locale #
        locale = await self.get_used_locale()
        try:
            # Open the locale file #
            with open(f"./locale/{locale}.json", "r",encoding="UTF-8") as f:
                locale = json.load(f)
                # Test for the meta key #
                if not "meta" in locale:
                    raise Exception(f"No meta key for locale file {locale}.")
        except Exception as e: # If this fails, presume there has been file corruption
            await self.reply(f":flag_gb: **Error:** The locale file for ``{locale}`` has been corrupted. Please contact the bot owner.\n"
                             f":flag_es: **Error:** El archivo de localización para ``{locale}`` ha sido dañado. Por favor, póngase en contacto con el propietario del bot.\n"
                             f":flag_fr: **Erreur:** Le fichier de localisation pour ``{locale}`` a été endommagé. Veuillez contacter le propriétaire du bot.\n"
                             f":flag_de: **Fehler:** Die Lokalisierungsdatei für ``{locale}`` wurde beschädigt. Bitte wenden Sie sich an den Botbesitzer.\n"
                             f":flag_nl: **Fout:** Het localisatiebestand voor ``{locale}`` is beschadigd. Neem contact op met de bot eigenaar.\n"
                             f":flag_pl: **Błąd:** Plik lokalizacji dla ``{locale}`` został uszkodzony. Skontaktuj się z właścicielem bota.\n"
                             )
            # Raise an error #
            raise Exception(f"Locale file for {locale} has been corrupted. {e}")
            return
                        
        try:
            # Get the message #
            message = locale[kwargs["message"]]
            # Delete the message key #
            del kwargs["message"]
        except:
            # If there is no message, presume it is yet to be translated. #
            message = locale["NotYetTranslated"]
            del kwargs["message"]
            
        try:
            # Format the message #
            message = message.format(**kwargs)
        except:
            # Yeah so apparently python doesn't like me just formatting the message without a try/except block. #
            pass

        # Return the message #
        return message

class LocalisedBot(AutoShardedBot):
    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

bot = LocalisedBot(command_prefix=get_prefix, intents=intents, log_level=None, activity=discord.Activity(name="with wires. Standby!"),status=discord.Status.dnd)

#bot = AutoShardedBot(command_prefix=get_prefix,intents=intents,log_level=logging.ERROR)
#bot = AutoShardedBot(command_prefix="fbb.",intents=intents,log_level=logging.ERROR)

bot.version = "arctic-sunrise-r2.0.0" #CODE-NAME-release-MAJOR.MINOR.PATCH

@bot.event
async def on_ready():
    # Grab the current epoch for statistic purposes #
    bot.marked_ready_at = time.time()
    
    # Assign database to bot #
    if os.getenv("DEPLOYMENT") == "STAGING":
        bot.db = db.staging
    elif os.getenv("DEPLOYMENT") == "PRODUCTION":
        bot.db = db.production
    else:
        bot.db = db.pre
    
    # Print out the Ready information #
    icon = from_image_file(img_path="assets/avatar_small.png",mode=Modes.TERMINAL)
    termcolor.cprint(f"Logged in as {bot.user.name}",'yellow')
    termcolor.cprint("Init...",'yellow')

    # Define the support server
    bot.support_server = discord.utils.get(bot.guilds,id=747145595558297663)
    bot.support_invite = "https://discord.gg/Mqcgca8"
    
    bot.database_active = True
    
    # Define the "main color" for embeds. Will mostly change for holidays (i.e Christmas, Halloween, NYD, etc) hence why it is a function. 
    def main_color():
        datenow = datetime.datetime.now()
        if datenow.month == 12:
            # If the day is before the 26th of December, return the Christmas color
            if datenow.day < 26:
                return discord.Color.from_rgb(255, 0, 0)
            else: # Otherwise, return the color for New Years Day (which is random.)
                return discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))   
        elif datenow.month == 10:
            if datenow.day >= 20:
                return discord.Color.from_rgb(235, 97, 35)
        elif datenow.month == 5 and datenow.day == 11: # Robyn's birthday
            return discord.Color.from_rgb(120,81,169)
        
        return discord.Colour.from_rgb(203, 153, 201)
    
    bot.main_color = main_color
    
    # Define all the badges available #
    bot.badges = {
        "developer": { # Made FB
            "icon": "👑",
            "description": "A developer of the bot.",
            "name": "Developer",
        },
        "translator": { # Translated the bot into a language
            "icon": "🌐",
            "description": "A translator for the bot.",
            "name": "Translator",
        },
        "contributor": { # Pushed a PR to the bot
            "icon": "👨‍💻",
            "description": "A contributor to the bot.",
            "name": "Contributor",
        },
        "teammember": { # Is a member of the FBS team
            "icon": "👨‍👩‍👧‍👦",
            "description": "A member of the FrostbyteSpace team.",
            "name": "Team Member",
        },
        "local58": { # 1/1000 chance on activating "help" command
            "icon": "📺",
            "description": "Do not be afraid of the dark.",
            "name": "Broadcast Concluded"
        },
        "americamoment": { # 1/100 chance on switching the language to "en_US"
            "icon": "🇺🇸",
            "description": "What's the difference anyway?",
            "name": "The American Moment"
        },
        "resonate": { # 10 days around the arctic sunrise release
            "icon": "🎶",
            "description": "The music never stops.",
            "name": "Bot.Discord.Frostbyte.2"
        },
        "mariahcarey": { # TODO
            "icon": "🎤",
            "description": "All she wants for Christmas is you.",
            "name": "Mariah Carey"
        },
        "botknowledges": { # Have ProtoByte and Frostbyte in the same server and witness them "talk" to each other
            "icon": "🤖",
            "description": "What are they planning?",
            "name": "Scheming"
        },
        "nohorny": { # Search for "frostbyte rating:e" on e621
            "icon": "🐴",
            "description": "PERV!",
            "name": "No horny!"
        },
        "articsunrise": { # Have a database record on Staging / Pre before ArticSunrise released
            "icon": "❄️",
            "description": "Used the Public Test Build (PTB) release of Frostbyte before Arctic Sunrise's release",
            "name": "Early Bird"
        }
    }
    
    # Define "important channels"
    bot.bot_log = discord.utils.get(bot.support_server.channels,id=850483854200012810) #bot-log on the main server
    bot.error_log = discord.utils.get(bot.support_server.channels,id=747145690563477504) #error-log on the main server
    bot.join_log = discord.utils.get(bot.support_server.channels,id=747145713498193991) #join-log on the main server
    debug_print(f"Set important channels")
    
    # Define internally and externally used emotes
    bot.internal_emotes = {}
    bot.internal_emotes["outage"] = discord.utils.get(bot.emojis,id=1026227194906812426)
    bot.internal_emotes["success"] = discord.utils.get(bot.emojis,id=747272333168869447)
    # bot.internal_emotes["error"] = discord.utils.get(bot.emojis,id=747272333168869447) #TODO
    # bot.internal_emotes["warning"] = discord.utils.get(bot.emojis,id=747272333168869447) #TODO
    # bot.internal_emotes["info"] = discord.utils.get(bot.emojis,id=747272333168869447) #TODO
    bot.internal_emotes["cross"] = discord.utils.get(bot.emojis,id=747272332904759407)
    bot.internal_emotes["neutral"] = discord.utils.get(bot.emojis,id=747272332158173385)
    debug_print(f"Set internal emotes")
    
    # Load all cogs
    debug_print(f"Loading cogs...")
    cogs = [x.replace(".py", "") for x in os.listdir("./core") if x.endswith(".py")]
    for cog in cogs:
        if cog != "main":
            try:
                await bot.load_extension(f"core.{cog}")
                debug_print(f"Loaded {cog}")
            except Exception as e:
                termcolor.cprint(f"Failed to load {cog}: {e}",'red')
                
    #termcolor.cprint("Started status loop")
    
    # Start the database integrity checker
    bot.loop.create_task(database_integrity_checker())
    #debug_print("Started database integrity checker")
    
    # Check if the webhook server is running by pinging it
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:6401/") as r:
                if r.status == 200:
                    debug_print("Webhook server is running.")
                else:
                    termcolor.cprint("Webhook server is not running.",'red')
                    termcolor.cprint("Ping returned a non-200 status code. Is the server running?",'red')
    except:
        termcolor.cprint("Webhook server is not running.",'red')
        termcolor.cprint("Ping failed. Is the server running?",'red')
                
    # Start the webhook updater, which will update the webhook server with the latest webhook data
    #bot.loop.create_task(webhook_updater())
    #termcolor.cprint("Started webhook updater",'green')
    
    # Print out the Ready information, as init is finished #
    termcolor.cprint("Init complete!",'green')
    to_terminal(icon)
    termcolor.cprint("-----------------------",'green')
    termcolor.cprint(f"Shards: {bot.shard_count}",'green')
    termcolor.cprint(f"Guilds: {len(bot.guilds)}",'green')
    termcolor.cprint(f"Users: {len(bot.users)}",'green')
    termcolor.cprint(f"Latency: {round(bot.latency*1000)}ms",'green')
    termcolor.cprint("-----------------------",'green')
    
    # Grab current time for uptime grabbing
    bot.started_at = time.time()
    
    # I don't know how to describe it but its self explanatory.
    bot.deployed = os.getenv("DEPLOYMENT")
    
    # Start the status loop
    bot.loop.create_task(status_task())
    
    
## No commands are defined in this file ##
# Due to how the help command works, it is not possible to define commands in this file. #
# If you want to define commands, please use a cog. #

# Guild join/leave events #
@bot.event
async def on_guild_join(guild):
    if not bot.is_ready():
        return
    # Add the guild to the database #
    # Duplicate the template and overwrite prefix and ID #
    new_template = db_template.copy()
    new_template["id"] = guild.id
    #new_template["prefix"] = await bot.get_prefix(bot, None) # i fucking hate positional arguments.
    if os.getenv("DEPLOYMENT").lower() == "production":
            new_template["prefix"] = "fb."
    elif os.getenv("DEPLOYMENT").lower() == "staging":
            new_template["prefix"] = "fbb."
    else:
            new_template["prefix"] = "fba."
            
    # If the guild is in the database already, do nothing. Otherwise, add it. #
    # This is to prevent the bot from overwriting the prefix if it is already in the database #
    if not bot.db.servers.find_one({"id": guild.id}):
        bot.db.servers.update_one({"id": guild.id}, {"$set": new_template},upsert=True)
    
    em = discord.Embed(title="Joined a new guild!", description=f"Guild name: {guild.name}\nGuild ID: {guild.id}\nMember count: {guild.member_count}\nShard ID: {guild.shard_id}", 
                       color=bot.main_color())
    em.set_thumbnail(url=guild.icon)
    em.set_footer(text=f"Guild owner: {guild.owner} ({guild.owner.id}) • Guild count: {len(bot.guilds)}")
    await bot.join_log.send(embed=em)
    
    # Send a message to the person who invited the bot, if possible (if the bot has audit log perms) #
    # This is a bit of a hacky way of doing it, but it works #
    target = None
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            if entry.target == bot.user:
                try:
                    target = entry.user
                except:
                    pass
        if target == None:
            raise Exception("No target found") # This is to make the except block run #
    except: # If the bot doesn't have audit log perms, just grab the first channel that isnt under a category called "Important" (case insensitive) and that the bot can send messages to #
        for channel in guild.channels:
            if not channel.category:
                if channel.permissions_for(guild.me).send_messages:
                    target = channel
                    break
            else:
                if channel.category.name.lower() != "important":
                    if channel.permissions_for(guild.me).send_messages:
                        target = channel
                        break
                
    if target:
        em = discord.Embed(title="Frostbyte",color=bot.main_color())
        # Load en_GB, fr_FR, nl_NL, pl_PL and de_DE for localization messages #
        with open("locale/en_GB.json") as f:
            en_GB = json.load(f)
        with open("locale/fr_FR.json") as f:
            fr_FR = json.load(f)
        with open("locale/es_ES.json") as f:
            es_ES = json.load(f)
        with open("locale/nl_NL.json") as f:
            nl_NL = json.load(f)
        # with open("locale/pl_PL.json") as f:
        #     pl_PL = json.load(f)
        with open("locale/de_DE.json") as f:
            de_DE = json.load(f)
            
        # I know this is really bad, but I don't know how to do it better #
        em.add_field(name=":flag_gb: :flag_us: :flag_ca: :flag_au: English", value=en_GB["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False)
        #em.add_field(name=":flag_fr: French", value=fr_FR["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False) # Uncomment when French is done
        em.add_field(name=":flag_es: Spanish", value=es_ES["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False)
        em.add_field(name=":flag_nl: Dutch", value=nl_NL["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False)
        #em.add_field(name=":flag_pl: Polish", value=pl_PL["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False) # Uncomment when Polish is done
        em.add_field(name=":flag_de: German", value=de_DE["JoinMessage"].format(prefix=new_template["prefix"], support=bot.support_invite), inline=False)
        
        em.set_thumbnail(url=bot.user.avatar)
        await target.send(embed=em)
        
@bot.event
async def on_guild_remove(guild):
    if not bot.is_ready():
        return
    # Remove the guild from the database #
    bot.db.servers.delete_one({"id": guild.id})
    
    em = discord.Embed(title="Left a guild!", description=f"Guild name: {guild.name}\nGuild ID: {guild.id}\nMember count: {guild.member_count}\nShard ID: {guild.shard_id}", 
                       color=bot.main_color())
    em.set_thumbnail(url=guild.icon)
    em.set_footer(text=f"Guild owner: {guild.owner} ({guild.owner.id}) • Guild count: {len(bot.guilds)}")
    await bot.join_log.send(embed=em)



@bot.event
async def on_message(ctx):
    if not bot.is_ready():
        return
    # Ignore messages from bots #
    if ctx.author.bot:
        return
    
    # NSFW Detection #
    # <3 DeepAI #
    for attatchment in ctx.attachments:
        # Check if the attatchment is an image #
        if attatchment.content_type.startswith("image/"):
            # Check if the guild has the NSFW filter enabled #
            if bot.db.servers.find_one({"id": ctx.guild.id})["nsfwFilter"]["enabled"] and not ctx.channel.nsfw:
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://api.deepai.org/api/nsfw-detector", data={"image": attatchment.url}, headers={"api-key": os.getenv("DEEP_AI"), "User-Agent": os.getenv("USER_AGENT")}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data["output"]["nsfw_score"] * 100 > bot.db.servers.find_one({"id": ctx.guild.id})["nsfwFilter"]["severity"] * 100:
                                await ctx.delete()
                                # As this is before the command handler, we need to open their locale file manually #
                                with open(f"locale/{bot.db.servers.find_one({'id': ctx.guild.id})['locale']}.json", "r") as f:
                                    locale = json.load(f)
                                
                                # Format the detections #
                                detections = ""
                                for detection in data["output"]["detections"]:
                                    detections += f"{detection['name']}: {round(float(detection['confidence']) * 100)}%\n"
                                if detections == "":
                                    detections = "None"
                                await ctx.channel.send(f"{ctx.author.mention} {locale['NSFWFilterMessage'].format(confidence=round(data['output']['nsfw_score'] * 100),detections=detections)}")
                                    
                                return
                            
    # Anti-Invite #
    try: # Because Python is Python, we need to do this #
        if bot.db.servers.find_one({"id": ctx.guild.id})["antiInvite"]["enabled"]:
            if "discord.gg/" in ctx.content.lower():
                await ctx.delete()
                await ctx.channel.send(f"{ctx.author.mention} {await ctx.get_locale(message='AntiInviteMessage')}")
                return
    except:
        pass 
    
    # Anti Caps Spam #
    try:
        if bot.db.servers.find_one({"id": ctx.guild.id})["antiCapsSpam"]["enabled"]:
            # If theres more than the specified amount of caps next to each other, delete the message #
            # Ignoring non-letters #
            caps = 0
            for char in ctx.content:
                if char.isupper():
                    caps += 1
                else:
                    if caps >= bot.db.servers.find_one({"id": ctx.guild.id})["antiCapsSpam"]["maxAllowed"]:
                        await ctx.delete()
                        await ctx.channel.send(f"{ctx.author.mention} {await ctx.get_locale(message='AntiCapsSpamMessage')}")
                        return
                    else:
                        caps = 0
    except:
        pass
    
    
    # Auto Response #
    if bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["enabled"]:
        for response in bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["responses"]:
            # As both responses and trigger can be either string or list, we need to check for both #
            # We also need to format for variables #
            if isinstance(response["response"], str):
                response["response"] = [response["response"]]
            if isinstance(response["trigger"], str):
                response["trigger"] = [response["trigger"]]
            for trigger in response["trigger"]:
                if trigger.lower() in ctx.content.lower():
                    await ctx.channel.send(random.choice(response["response"]) % {
                        "user": ctx.author.mention, 
                        "server": ctx.guild.name, 
                        "channel": ctx.channel.mention, 
                        "message": ctx.message.link, 
                        "prefix": bot.db.servers.find_one({"id": ctx.guild.id})["prefix"]
                        }) # Quite an old way of doing this, but it works #
                    # We can continue here, as this doesn't effect the command handler #
    
    # Pass the message to the command handler #
    if ctx.content.startswith(bot.db.servers.find_one({"id": ctx.guild.id})["prefix"]):
        async with ctx.channel.typing():
            await bot.process_commands(ctx)

# Config events #
@bot.event
async def on_member_update(before, after):
    if not bot.is_ready():
        return
    # Anti-hoist #
    if bot.db.servers.find_one({"id": before.guild.id})["antiHoist"]:
        if before.display_name != after.display_name:
            # If the user has a role that is higher than the bot, ignore them #
            if after.top_role > after.guild.me.top_role:
                return
            # Check for punctuation in the first three characters. If there is, change the name back #
            if after.display_name[0] in string.punctuation or after.display_name[1] in string.punctuation or after.display_name[2] in string.punctuation:
                await after.edit(nick="hoister no more 🛎️🛎️")
                # As this is before the command handler, we need to open their locale file manually #
                with open(f"locale/{bot.db.servers.find_one({'id': after.guild.id})['locale']}.json", "r") as f:
                    locale = json.load(f)
                await after.send(locale["AntiHoistMessage"].format(guild=after.guild.name))

@bot.event
async def on_member_join(member):
    if not bot.is_ready():
        return
    # First, ignore bots #
    if member.bot:
        return
    # Raid Mode #
    if bot.db.servers.find_one({"id": member.guild.id})["raidMode"]["enabled"]:
        # Check if the Force "kickNewMembers" option is enabled #
        if bot.db.servers.find_one({"id": member.guild.id})["raidMode"]["forces"]["kickNewMembers"]:
            await member.send(f"Raid Mode is enabled in {member.guild.name}. You have been kicked. Please try again later.")
            await member.kick(reason="Raid Mode")
            return
    
    # Welcome #
    if bot.db.servers.find_one({"id": member.guild.id})["welcome"]["enabled"]:
        channel = member.guild.get_channel(bot.db.servers.find_one({"id": member.guild.id})["welcome"]["channel"])
        # Generate the welcome image #
        generated = await image_generation.generate_welcome_image(member, member.guild, None)
        # Then send it #
        await channel.send(file=discord.File(generated, "welcome.png"), content=member.mention)

@bot.event
async def on_member_remove(member):
    # First, ignore bots #
    if member.bot:
        return
    
    if not bot.is_ready():
        return
    
    # Leave #
    if bot.db.servers.find_one({"id": member.guild.id})["leave"]["enabled"]:
        channel = member.guild.get_channel(bot.db.servers.find_one({"id": member.guild.id})["leave"]["channel"])
        # Generate the leave image #
        generated = await image_generation.generate_leave_image(member, member.guild)
        #generated = "./assets/placeholder.png"
        # Then send it #
        await channel.send(file=discord.File(generated, "leave.png"))

@bot.event # Retrigger the on_message event when a message is edited #
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    bot.dispatch("message", after) # We *could* use .process_commands() here, but that would pose the risk of bypassing the NSFW filter and anti-invite #

# Error Handler #
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        closest_match = difflib.get_close_matches(ctx.invoked_with, [command.name for command in bot.commands])
        if closest_match:
            #await ctx.reply(f'Command ``"{ctx.invoked_with}"`` not found. Did you mean ``"{closest_match[0]}"``?')
            await ctx.send_locale(message="CommandNotFoundClosestMatch",command=ctx.invoked_with,closest_match=closest_match[0])    
        else:
            #await ctx.reply(f'Command ``"{ctx.invoked_with}"`` not found.')
            await ctx.send_locale(message="CommandNotFound",command=ctx.invoked_with)
    elif isinstance(error, commands.MissingRequiredArgument):
        #await ctx.reply("Missing required argument")
        await ctx.send_locale(message="MissingRequiredArgument")
    elif isinstance(error, commands.MissingPermissions):
        #await ctx.reply("You don't have the required permissions to run this command")
        await ctx.send_locale(message="MissingPermissions")
    elif isinstance(error, commands.BotMissingPermissions):
        #await ctx.reply("I don't have the required permissions to run this command")
        await ctx.send_locale(message="BotMissingPermissions")
    elif isinstance(error, commands.NotOwner):
        await ctx.reply(":face_with_raised_eyebrow::camera_with_flash:")
        em = discord.Embed(title="Caught in 4k",description=f"{ctx.author} was caught in 4k.\nCommand: ``{ctx.message.content}``",color=0x00ff00,timestamp=datetime.datetime.utcnow())
        em.set_thumbnail(url=ctx.author.avatar)
        em.set_footer(text="They tried to run an owner-only command. What a dummy.")
        await bot.bot_log.send(embed=em)
    elif isinstance(error, commands.CommandOnCooldown):
        #await ctx.reply(f"This command is on cooldown. Try again in {round(error.retry_after, 2)} seconds")
        await ctx.send_locale(message="CommandOnCooldown",retry_after=round(error.retry_after, 2))
    elif isinstance(error, NotImplementedError):
        #await ctx.reply("This command is not implemented yet")
        await ctx.send_locale(message="NotImplemented")
    else:
        # Generate a random ID
        # This'll be used to grab the dump and identify the error later
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        tb = traceback.TracebackException.from_exception(error)
        tb = ''.join(tb.format())
        error_em = discord.Embed(title="500: Internal Protogen Error", description=await ctx.get_locale(message="CommandErrorDescription"), color=0xff0000)
        error_em.set_footer(text=f"If this continues happening, please join the support server! • Error ID: {id}")
        try:
            if commands.is_owner():
                if len(tb) > 1024:
                    # If the traceback is too long, send it as a file #
                    with open("error.txt", "w") as f:
                        f.write(tb)
                    await ctx.reply(file=discord.File("error.txt"))
                    os.remove("error.txt")
                    tb = "Traceback too long to send in chat. Sent as a file."
                error_em.add_field(name="Error", value=f"```py\n{tb}```")
        except: 
            pass
        await ctx.reply(embed=error_em)
        # If the owner ran the command, abort, as we don't want to log the error #
        # if commands.is_owner():
        #    return
        if ctx.author.id == 478675118332051466 or ctx.author.id == 659488296820408355: # I hate this but it's the only way to do it #
            return

        # This is where shit gets complicated. #
        # We need to "compile" a "error dump", add it to the database with an ID, then send it to the channel, with some contextual information #
        # This should provide as much information as possible, while also being easy to read #
        # Sort of like a crash dump #
        
        # The error dump will be a dictionary, with the following
        # id: The ID of the error dump
        # traceback: The traceback
        # command: The command that was run
        # point: The line of code that the error occured on, if possible
        # user: The user that ran the command
        # time: The time the error occured
        # guild: The guild the command was run in, if applicable
        # link: The link to the message that the command was run in, if applicable
        # locale: The locale that the guild (or user) is using, if applicable
        # sysinfo: A full list of system information, including OS, all library versions, CPU/RAM usage, etc.
        # 
        # The error dump will be stored in the database, and the ID will be sent to the channel.
        
        dump = {}
        dump["id"] = id
        
        # Get the line of code that the error occured on #
        point = None
        for line in tb.splitlines():
            if line.startswith("  File"):
                point = line
                break
        dump["point"] = point
                
        # Get the locale #
        locale = None
        try:
            locale = await ctx.get_used_locale()
        except:
            locale = "fallback"
        dump["locale"] = locale
        
        # Get the system info #
        dump["sysinfo"] = {}
        
        # Now, before we get the system info, we need to get the library versions #
        dump["sysinfo"]["lib_versions"] = {}
        dump["sysinfo"]["lib_versions"]["discord.py"] = discord.__version__
        dump["sysinfo"]["lib_versions"]["aiohttp"] = aiohttp.__version__
        dump["sysinfo"]["lib_versions"]["psutil"] = psutil.__version__
        
        # Now, we can get the system info #
        dump["sysinfo"]["os"] = str(platform.platform())
        dump["sysinfo"]["cpu"] = str(psutil.cpu_percent(interval=1)) + "%"
        dump["sysinfo"]["ram"] = str(psutil.virtual_memory().percent) + "%"
        dump["sysinfo"]["disk"] = str(psutil.disk_usage('/').percent) + "%"
        dump["sysinfo"]["uptime"] = str(datetime.timedelta(seconds=round(psutil.boot_time())))
        
        # Get Python version #
        dump["sysinfo"]["python"] = str(platform.python_version())
        
        # Now, we can add the rest of the info #
        dump["traceback"] = tb
        dump["command"] = ctx.message.content
        dump["user"] = {"id": ctx.author.id, "name": str(ctx.author)}
        dump["time"] = datetime.datetime.utcnow().isoformat()
        if ctx.guild:
            dump["guild"] = {"id": ctx.guild.id, "name": str(ctx.guild)}
            dump["link"] = ctx.message.jump_url
            
        # And viola! We have a full error dump! #
        # Now, we can add it to the database #
        try:
            bot.db.error_dumps.insert_one(dump)
        except: # If the database is down, add it to a file instead #
            # This is a full last resort, as it will be overwritten on any future errors #
            # We will also need to manually make sure that the file is deleted when the database is reachable again #
            # All whilst creatin the file ourselves #
            with open("error_dump.json", "w") as f:
                json.dump(dump, f, indent=4)
            
        
        # And finally, we can send the ID to the channel #
        # We'll also send the original error message #
        # If the error seems to be "fatal", we'll @everyone (TODO) #
        error_em = discord.Embed(title="Error Report", description=f"```py\n{error}```", color=0xff0000, timestamp=datetime.datetime.utcnow())
        error_em.set_footer(text=f"Error Dump ID: {id}")
        error_em.add_field(name="Command", value=f"``{ctx.message.content}``")
        error_em.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})")
        if locale != "fallback":
            # As always, grab the flag and language name from the locale
            with open(f"./locale/{locale}.json", "r") as f:
                locale = json.load(f)
            error_em.add_field(name="Locale", value=f'{locale["meta"]["flag"]} {locale["meta"]["english_name"]}')
        else:
            error_em.add_field(name="Locale Set", value="N/A (Not Set or Failed to Get)")
            
        error_em.set_thumbnail(url=ctx.author.avatar)
        
        await bot.error_log.send(embed=error_em)

        
# Check for launch arguments i.e --pre, --production, etc #
for arg in sys.argv:
    if arg == "--production":
        os.environ["DEPLOYMENT"] = "PRODUCTION"
    elif arg == "--pre":
        os.environ["DEPLOYMENT"] = "PRE"
    elif arg == "--staging":
        os.environ["DEPLOYMENT"] = "STAGING"
        


# Run the bot #
if os.getenv("DEPLOYMENT") == "STAGING":
    bot.run(os.getenv("TOKEN_STAGING"))
elif os.getenv("DEPLOYMENT") == "PRE":
    bot.run(os.getenv("TOKEN_PRE"))
elif os.getenv("DEPLOYMENT") == "PRODUCTION":
    bot.run(os.getenv("TOKEN_PRODUCTION"))
else:
    termcolor.cprint("No deployment specified. Aborting...",'red')