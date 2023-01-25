import aiohttp
import aiohttp
import asyncio
import discord
from discord.ext import commands
import os
import json
import random

with open('./locale/countries.json', 'r') as f:
    countries = json.load(f)

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(brief="User configuration commands",invoke_without_command=True)
    async def userconfig(self, ctx):
        # Change the message content to "userconfig show" and dispatch it
        # Hacky yes, but it works
        ctx.message.content = f'{self.bot.db.servers.find_one({"id": ctx.guild.id})["prefix"]}userconfig show'
        self.bot.dispatch("message", ctx.message)
        
    @userconfig.command(brief="Shows your current user configuration")
    async def show(self, ctx):
        config = self.bot.db.users.find_one({"id": ctx.author.id})
        if not config:
            self.bot.db.users.insert_one({"id": ctx.author.id, "country": "Unknown"})
            config = self.bot.db.users.find_one({"id": ctx.author.id})
        
        em = discord.Embed(title=await ctx.get_locale(message="UserConfigTitle"), description=await ctx.get_locale(message="UserConfigDescription"), color=self.bot.main_color())
        
        em.add_field(name=await ctx.get_locale(message="UserConfigCountryTitle"), value=config["country"])
        try:
            # Open the language file and get the language name and flag #
            with open(f"locale/{config['language']}.json") as f:
                lang = json.load(f)
            
            flag = lang["meta"]["flag"]
            denonym = lang["meta"]["denonym"]
            
            em.add_field(name=await ctx.get_locale(message="UserConfigLanguageTitle"), value=f"{flag} {denonym}")
        except: pass # No language set
        
        em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1030143502912344114/1067460562709139536/Frostbyte-Userconfig.png")
        
        await ctx.send(embed=em)
        
    @userconfig.command(brief="Shows (or sets) your current preffered language",name="language")
    async def usr_language(self, ctx,*, language=None):
        config = self.bot.db.users.find_one({"id": ctx.author.id})
        if not config:
            self.bot.db.users.insert_one({"id": ctx.author.id, "language": "en_GB"})
            config = self.bot.db.users.find_one({"id": ctx.author.id})
            
        try: # I fucking hate Python at times
            if not config["language"]:
                self.bot.db.users.insert_one({"id": ctx.author.id, "language": "en_GB"})
                config = self.bot.db.users.find_one({"id": ctx.author.id})
        except KeyError:
            self.bot.db.users.insert_one({"id": ctx.author.id, "language": "en_GB"})
            config = self.bot.db.users.find_one({"id": ctx.author.id})
        except Exception as e: raise e
        
        if not language:
            # Open the language file and get the language name #
            with open(f"locale/{config['language']}.json") as f:
                lang = json.load(f)
            await ctx.send_locale(message="UserConfigLanguageCurrent", lang=lang["meta"]["denonym"])
        elif language == "list":
          # Invoke the command "language list", to save on time, while bypassing checks #
          await self.bot.invoke(ctx, "config language list")
        # elif language == config["language"]:
        #     await ctx.send_locale(message="UserConfigLanguageAlreadySet",lang=language)
        else:
            # Check if the language exists #
            if os.path.isfile(f"locale/{language}.json"):
                self.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"language": language}})
                await ctx.send_locale(message="UserConfigLanguageSet", lang=language)
            else:
                await ctx.send_locale(message="UserConfigLanguageInvalid")
                
    @userconfig.command(brief="Shows (or sets) your country. Used for currency, timezone and default language.")
    async def country(self, ctx,*, country=None):
        config = self.bot.db.users.find_one({"id": ctx.author.id})
        if not config:
            self.bot.db.users.insert_one({"id": ctx.author.id, "country": "Unknown"})
            config = self.bot.db.users.find_one({"id": ctx.author.id})
        if not country:
            await ctx.send_locale(message="UserConfigCountryCurrent", country=config["country"])
        else: # Compare the country provided to a list of countries at the start of the file. #
            if country in countries:
                self.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"country": country}})
                await ctx.send_locale(message="UserConfigCountrySet", country=country)
            else:
                # Format to make the countires more human readable #
                # First, sort all the countries by their continent, provided in their timezone prefix (before the /) #
                # Then, append their flag to the start of the country name #
                # Finally, join them all together with a newline between each one #
                # Continents will be seperated by fields, with the continent name as the field name #
                continents = {}
                for c in countries:
                    if countries[c]["timezone"].split("/")[0] not in continents:
                        continents[countries[c]["timezone"].split("/")[0]] = []
                    continents[countries[c]["timezone"].split("/")[0]].append(f"{countries[c]['flag']} {c}")
                for c in continents:
                    continents[c] = "\n".join(sorted(continents[c]))
                # Create an embed with the list of countries #
                embed = discord.Embed(title=await ctx.get_locale(message="UserConfigCountryListTitle"), description=await ctx.get_locale(message="UserConfigCountryListDescription"),color=self.bot.main_color())
                for c in continents:
                    embed.add_field(name=c, value=continents[c])
                await ctx.send(embed=embed)
                  
    @commands.has_guild_permissions(manage_guild=True)
    @commands.group(brief="Server configuration commands", invoke_without_command=True,name="serverconfig",aliases=["config"])
    async def config(self, ctx):
        config = self.bot.db.servers.find_one({"id": ctx.guild.id})
        em = discord.Embed(title=await ctx.get_locale(message="ConfigTitle"), description=await ctx.get_locale(message="ConfigDescription") ,color=self.bot.main_color())
        em.add_field(name=await ctx.get_locale(message="ConfigPrefixTitle"), value=config["prefix"])
        em.add_field(name=await ctx.get_locale(message="ConfigNSFWTitle"), value=(await ctx.get_locale(message="Active") if config["nsfwFilter"]["enabled"] else await ctx.get_locale(message="Inactive")))
        with open(f"./locale/{config['locale']}.json", "r") as f:
            lang = json.load(f)
        em.add_field(name=await ctx.get_locale(message="ConfigLanguageTitle"), value=f"{lang['meta']['flag']} {lang['meta']['denonym']}")
        em.add_field(name=await ctx.get_locale(message="ConfigAntiHoistTitle"), value=(await ctx.get_locale(message="Active") if config["antiHoist"]["enabled"] else await ctx.get_locale(message="Inactive")))
        em.add_field(name=await ctx.get_locale(message="ConfigAntiInviteTitle"), value=(await ctx.get_locale(message="Active") if config["antiInvite"]["enabled"] else await ctx.get_locale(message="Inactive")))
        #em.add_field(name=await ctx.get_locale(message="ConfigRaidModeTitle"), value=(await ctx.get_locale(message="Active") if config["raidMode"]["enabled"] else await ctx.get_locale(message="Inactive")))
        # TODO: Finish raid mode.
        em.add_field(name=await ctx.get_locale(message="ConfigWelcomeTitle"), value=(f"{await ctx.get_locale(message='Active')} (<#{config['welcome']['channel']}>)" if config["welcome"]["enabled"] else await ctx.get_locale(message="Inactive")))
        em.add_field(name=await ctx.get_locale(message="ConfigLeaveTitle"), value=(f"{await ctx.get_locale(message='Active')} (<#{config['leave']['channel']}>)" if config["leave"]["enabled"] else await ctx.get_locale(message="Inactive")))
        em.add_field(name=await ctx.get_locale(message="ConfigAntiCapsTitle"), value=(await ctx.get_locale(message="Active") if config["antiCapsSpam"]["enabled"] else await ctx.get_locale(message="Inactive")))
        em.add_field(name=await ctx.get_locale(message="ConfigAutoResponseTitle"), value=f"{await ctx.get_locale(message='Active')} ({len(config['autoResponse']['responses'])} responses)" if config["autoResponse"]["enabled"] else await ctx.get_locale(message="Inactive"))
        em.add_field(name=await ctx.get_locale(message="ConfigModLogTitle"), value=(f"{await ctx.get_locale(message='Active')} (<#{config['modLog']['channel']}>)" if config["modLog"]["enabled"] else await ctx.get_locale(message="Inactive")))
        
        # Padding
        em.add_field(name="\u200b", value="\u200b")
        em.add_field(name="\u200b", value="\u200b")
        
        em.set_thumbnail(url="https://media.discordapp.net/attachments/1030143502912344114/1067448197267603526/Frostbyte-Config.png")
        
        
        await ctx.send(embed=em)
        
    @commands.has_guild_permissions(manage_guild=True)
    @config.command(brief="Sets the server's prefix")
    async def prefix(self, ctx, prefix = None):
        if prefix == None:
            await ctx.send_locale(message="PrefixCurrent", prefix=self.bot.db.servers.find_one({"id": ctx.guild.id})["prefix"])
            return
        self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"prefix": prefix}})
        await ctx.send_locale(message="PrefixSet", prefix=prefix)
        
    @commands.has_guild_permissions(manage_guild=True)
    @config.command(brief="Sets the server's language")
    async def language(self, ctx, lang = None):
        if lang == None:
            await ctx.send_locale(message="LanguageCurrent", lang=self.bot.db.servers.find_one({"id": ctx.guild.id})["locale"])
            return
        # Replace any dashes to underscore to make it easier to type #
        lang = lang.replace("-", "_")
        # If the language is the same as the current one, don't do anything #
        if lang == self.bot.db.servers.find_one({"id": ctx.guild.id})["locale"]:
            await ctx.send_locale(message="LanguageAlreadySet")
            return

        # Check if the language is valid by checking if the file exists, excluding fallback #
        if os.path.isfile(f"locale/{lang}.json") and lang != "fallback":
            # Add a 1 in 100 chance of the bot saying "America moment." when switching to en-US #
            if lang == "en-US" and random.randint(1, 100) == 1:
                await ctx.send_locale(message="LanguageUSAEasterEgg")
                # Then add a badge. #
                badges = self.bot.db.users.find_one({"id": ctx.author.id})["badges"]
                # If the user already has the badge, do nothing #
                if "americamoment" not in badges:
                    badges.append("americamoment")
                    self.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"badges": badges}})
                    await ctx.author.send("You have been awarded the **The American Moment** badge.\nWhy would you switch to this language?")
                
            # If the language is not 100% translated, ask for confirmation #
            with open(f"locale/{lang}.json", "r") as f:
                locale = json.load(f)
                
            with open("locale/en_GB.json", "r") as f2:
                en_gb = json.load(f2)
                translated = 0
                for key in en_gb:
                    if key in locale:
                        translated += 1
                translated = round((translated / len(en_gb)) * 100,2)
                
            if translated < 100:
                await ctx.send_locale(message="LanguageNotTranslated", translated=translated,totalKeys=len(locale) - 1,fullTotal=len(en_gb) -1) # -1 because of the meta key
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send_locale(message="LanguageNotTranslatedTimeout")
                    return
                if msg.content.lower() not in ["yes", "y", "ye", "yeah", "yep", "yup","ja", "oui", "si", "tak", "ja"]:
                    await ctx.send_locale(message="LanguageNotTranslatedNo")
                    return
                
            # Update the database #
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"locale": lang}})
            await ctx.send_locale(message="LanguageSet", lang=lang)

        else:
            # If the language is "list", list all available languages, using the flag and country as defined in the locale file. #
            # Flag and country are in the "meta" section of the locale file. #
            if lang == "list":
                em = discord.Embed(title=await ctx.get_locale(message="LanguageListTitle"),description=await ctx.get_locale(message="LanguageListDescription"), color=self.bot.main_color())
                # Sort by long name, not language code #
                # This is done by loading the locale file and getting the name from the "meta" section #
                sort = []
                for file in sorted(os.listdir("locale")):
                    if file.endswith(".json") and file != "fallback.json" and file != "countries.json":
                        with open(f"locale/{file}", "r", encoding="UTF-8") as f:
                            locale = json.load(f)
                            sort.append((locale["meta"]["name"], file))
                sort = sorted(sort, key=lambda x: x[0])
                
                for file in sort:
                    file = file[1]
                    if file.endswith(".json") and file != "fallback.json" and file != "countries.json":
                        with open(f"locale/{file}", "r", encoding="UTF-8") as f:
                            locale = json.load(f)
                            # Determine how "translated" the language is by checking how many strings are translated compared to en-GB #
                            # en-GB is the default language, so it will always be 100% translated. #
                            with open("locale/en_GB.json", "r") as f2:
                                en_gb = json.load(f2)
                                translated = 0
                                for key in en_gb:
                                    if key in locale:
                                        translated += 1
                                translated = round((translated / len(en_gb)) * 100,2)
                            em.add_field(name=f"{locale['meta']['flag']} {locale['meta']['name']} ({locale['meta']['short_name']})", value=f"`{file[:-5]}` "
                                         f"{f'({translated}% translated)' if translated != 100 else ''}",inline=False)
                await ctx.send(embed=em)
            else:
                # Check if there is a closest match to the language, using difflib.get_close_matches #
                # If there is, ask the user if they meant that language. #
                # If not, tell them the language is invalid. #
                matches = difflib.get_close_matches(lang, [file[:-5] for file in os.listdir("locale") if file.endswith(".json") and file != "fallback.json"],cutoff=0.45)
                if matches:
                    #await ctx.send(f"Invalid language. Did you mean `{matches[0]}`?")
                    # Quickly open the locale file to get the language name #
                    with open(f"locale/{matches[0]}.json", "r", encoding="UTF-8") as f:
                        locale = json.load(f)

                    await ctx.send_locale(message="LanguageInvalidCloseMatch", language=matches[0], flag=locale["meta"]["flag"], short_name=locale["meta"]["short_name"])
                else:
                    #await ctx.send("Invalid language. To see a list of available languages, use `language list`")
                    await ctx.send_locale(message="LanguageInvalid")
                    
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_messages=True)
    @config.command(brief="Toggles the NSFW filter, or sets it to a specific severity")
    async def nsfw(self, ctx, severity = None):
        if severity == None:
            await ctx.send_locale(message="NSFWCurrent", severity=self.bot.db.servers.find_one({"id": ctx.guild.id})["nsfwFilter"]["severity"])
            return
        if severity == "off":
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"nsfwFilter": {"enabled": False, "severity": 0}}})
            await ctx.send_locale(message="NSFWSet", severity=0)
            return
        try:
            severity = int(severity)
            if severity < 0 or severity > 100:
                await ctx.send_locale(message="NSFWInvalid")
                return
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"nsfwFilter": {"enabled": True, "severity": severity / 100}}})
            await ctx.send_locale(message="NSFWSet", severity=severity)
        except ValueError:
            await ctx.send_locale(message="NSFWInvalid")
            
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_nicknames=True)
    @commands.has_guild_permissions(manage_nicknames=True)
    @config.command(brief="Toggles the anti-hoist filter")
    async def antihoist(self, ctx):
        self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"antiHoist": not self.bot.db.servers.find_one({"id": ctx.guild.id})["antiHoist"]}})
        await ctx.send_locale(message="AntiHoistSet", enabled=not self.bot.db.servers.find_one({"id": ctx.guild.id})["antiHoist"])
        
    @commands.has_guild_permissions(manage_guild=True)
    @config.command(brief="Sets (or disables) the welcome channel")
    async def welcome(self, ctx, *, channel : discord.TextChannel = None):
        if channel == None:
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"welcome": {"enabled": False, "channel": None}}})
            await ctx.send_locale(message="WelcomeDisabled")
        else:
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"welcome": {"enabled": True, "channel": channel.id}}})
            await ctx.send_locale(message="WelcomeSet", channel=channel.mention)
    
    @commands.has_guild_permissions(manage_guild=True)
    @config.command(brief="Sets (or disables) the leave channel")
    async def leave(self, ctx, *, channel : discord.TextChannel = None):
        if channel == None:
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"leave": {"enabled": False, "channel": None}}})
            await ctx.send_locale(message="LeaveDisabled")
        else:
            self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"leave": {"enabled": True, "channel": channel.id}}})
            await ctx.send_locale(message="LeaveSet", channel=channel.mention)
            
    @commands.has_guild_permissions(manage_guild=True)
    @config.group(brief="Commands for configuring the bot's auto responses", invoke_without_command=True)
    async def autoresponse(self, ctx):
        # List all auto responses #
        # If there are none, tell the user #
        responses = self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["responses"]
        if len(responses) == 0:
            await ctx.send_locale(message="AutoResponseListEmpty")
            return
        # Otherwise, list them #
        # Making sure to list the placeholder variables #
        em = discord.Embed(title="Auto Responses", description="List of all auto responses for this server", color=self.bot.main_color())
        
        for response in responses:
            # Add a condition to format the trigger and response if its an array (an OR response) #
            # Bare in mind there can be multiple OR responses #
            if type(response["trigger"]) == list:
                trigger = "``" + "`` OR ``".join(response["trigger"]) + "``"
            else:
                trigger = response["trigger"]
            if type(response["response"]) == list:
                response = "``" + "`` OR ``".join(response["response"]) + "``"
            else:
                response = "``" + response["response"] + "``"
            em.add_field(name=trigger, value=response, inline=False)
            
        em.set_footer(text=f"Use ``{ctx.prefix}config autoresponse <add|remove|edit>`` to manage auto responses")
        await ctx.send(embed=em)
        
    @commands.has_guild_permissions(manage_guild=True)
    @autoresponse.command(brief="Adds an auto response")
    async def add(self, ctx, trigger, *, response):
        # Make sure the trigger isn't too long #
        if len(trigger) > 100:
            await ctx.send_locale(message="AutoResponseTriggerTooLong")
            return
        # Make sure the response isn't too long #
        if len(response) > 500:
            await ctx.send_locale(message="AutoResponseResponseTooLong")
            return
        # Make sure the trigger isn't too short #
        if len(trigger) < 1:
            await ctx.send_locale(message="AutoResponseTriggerTooShort")
            return
        # Make sure the response isn't too short #
        if len(response) < 1:
            await ctx.send_locale(message="AutoResponseResponseTooShort")
            return
        # Make sure the trigger doesn't already exist #
        for response in self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["responses"]:
            if response["trigger"] == trigger:
                await ctx.send_locale(message="AutoResponseTriggerExists")
                return
        # Add the response #
        self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$push": {"autoResponse": {"trigger": trigger, "response": response}}})
        await ctx.send_locale(message="AutoResponseAdded", trigger=trigger)
        
    @commands.has_guild_permissions(manage_guild=True)
    @autoresponse.command(brief="Removes an auto response")
    async def remove(self, ctx, *, trigger):
        # Make sure the trigger exists #
        for response in self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["responses"]:
            if response["trigger"] == trigger:
                # Remove the response #
                self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$pull": {"autoResponse": {"trigger": trigger, "response": response["response"]}}})
                await ctx.send_locale(message="AutoResponseRemoved", trigger=trigger)
                return
        # Otherwise, tell the user #
        await ctx.send_locale(message="AutoResponseTriggerDoesntExist")
        
    @commands.has_guild_permissions(manage_guild=True)
    @autoresponse.command(brief="Edits an auto response")
    async def edit(self, ctx, trigger, *, response):
        # Make sure the trigger exists #
        for response in self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["responses"]:
            if response["trigger"] == trigger:
                # Make sure the response isn't too long #
                if len(response) > 500:
                    await ctx.send_locale(message="AutoResponseResponseTooLong")
                    return
                # Make sure the response isn't too short #
                if len(response) < 1:
                    await ctx.send_locale(message="AutoResponseResponseTooShort")
                    return
                # Update the response #
                self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"autoResponse.$[elem].response": response}}, array_filters=[{"elem.trigger": trigger}])
                await ctx.send_locale(message="AutoResponseEdit", trigger=trigger)
                return
        
        # Otherwise, tell the user #
        await ctx.send_locale(message="AutoResponseTriggerDoesntExist")
    
    @commands.has_guild_permissions(manage_guild=True)
    @autoresponse.command(brief="Toggles auto responses")
    async def toggle(self, ctx):
        # Toggle auto responses #
        self.bot.db.servers.update_one({"id": ctx.guild.id}, {"$set": {"autoResponse.enabled": not self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["enabled"]}})
        # Tell the user #
        if self.bot.db.servers.find_one({"id": ctx.guild.id})["autoResponse"]["enabled"]:
            await ctx.send_locale(message="AutoResponseEnabled")
        else:
            await ctx.send_locale(message="AutoResponseDisabled")
            
    @commands.has_guild_permissions(manage_guild=True)
    @config.group(brief="Commands for moderation logging")
    async def logging(self, ctx):
        if ctx.invoked_subcommand is None:
            # If the subcommand is None, show the logging config #
            # Get the logging config #
            config = self.bot.db.servers.find_one({"id": ctx.guild.id})["modLog"]
            # Make the embed #
            em = discord.Embed(title="Logging", description="This server's logging configuration", color=self.bot.main_color())
            em.add_field(name="Enabled", value=config["enabled"])
            em.add_field(name="Channel", value=ctx.guild.get_channel(config["channel"]).mention if config["channel"] else "None")
            em.add_field(name="Events", value="``" + "`` ``".join(config["modular"]) + "``" if config["modular"] else "None")
            em.set_footer(text=f"Use ``{ctx.prefix}config logging <enable|disable|channel|events>`` to manage logging")
            await ctx.send(embed=em)
                
        
async def setup(bot):
    await bot.add_cog(Configuration(bot))