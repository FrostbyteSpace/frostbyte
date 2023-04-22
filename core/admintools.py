import aiohttp
import asyncio
import discord
from discord.ext import commands
import os
import inspect
import ast
import json
from utils import image_generation
import time


class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(brief="Reloads all cogs")
    async def reload(self, ctx, *, cogs: str = "all"):
        success, fails = [], []
        if cogs == "all":
            cogs = [x.replace(".py", "") for x in os.listdir("./core") if x.endswith(".py")]
        else:
            cogs = cogs.split(", ")
        msg = await ctx.reply(f"Reloading {len(cogs)} cogs..")
        for cog in cogs:
            try:
                await self.bot.reload_extension(f"core.{cog}")
                success.append(cog)
            except Exception as e:
                fails.append(str(e))
        sstr = "\n".join(success)
        fstr = "\n".join(fails)
        await msg.edit(content=None,embed=discord.Embed(description=f"Successfully reloaded {len(success)} cog{'s' if len(success) != 1 else ''}."
            f"\n```\n{sstr}\n```"*(len(success)>0)+f"And failed to reload {len(fails)} cog{'s' if len(fails) != 1 else ''}.\n```\n{fstr}\n```"*(len(fails)>0),
                                                        color=self.bot.main_color()))
    
    @commands.is_owner()
    @commands.command()
    async def sudo(self, ctx, user: discord.Member, *, command: str):
        message = ctx.message
        message.author = user
        message.content = command
        await self.bot.process_commands(message)
        await ctx.message.add_reaction(discord.utils.get(self.bot.emojis, id=747272333168869447))
    
    @commands.is_owner()
    @commands.command(name='eval', brief="Evaluates code")
    async def _eval(self, ctx: discord.ext.commands.Context, *, cmd: str):
        """ Evaluates python code! """
        env = {
            'ctx': ctx,
            'bot': self.bot,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource,
            'commands': commands,
            "discord": discord
        }
        
        def insert_returns(body):
            # insert return stmt if the last expression is a expression statement
            if isinstance(body[-1], ast.Expr):
                body[-1] = ast.Return(body[-1].value)
                ast.fix_missing_locations(body[-1])

            # for if statements, we insert returns into the body and the orelse
            if isinstance(body[-1], ast.If):
                insert_returns(body[-1].body)
                insert_returns(body[-1].orelse)

            # for with blocks, again we insert returns into the body
            if isinstance(body[-1], ast.With):
                insert_returns(body[-1].body)
    
        try:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            
            # remove code block language indicator if present
            if cmd.startswith("py"):
                cmd = "\n".join(cmd.splitlines()[1:])

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
        except Exception as e:
            result = e
            
        if result == None:
            result = "No Output"
        
        em = discord.Embed(title="Evaluation", description=f"```py\n{result}```", color=self.bot.main_color())
        await ctx.send(embed=em)
    
    @commands.is_owner()
    @commands.command(name="shardinfo", brief="Shows guild, user and ping info for each shard")
    async def shardinfo(self, ctx):
        shards = []
        for i in range(self.bot.shard_count):
            shard = self.bot.get_shard(i)
            guilds = 0
            users = 0
            for x in self.bot.guilds:
                if x.shard_id == i:
                    guilds += 1
                    users += len(x.members)
            
            latency = round(shard.latency * 1000, 2)
            # Prefix the shard depending on the latency. This is to make it easier to see which shards are lagging.
            if latency > 400:
                latency = f"**{self.bot.internal_emotes['outage']} {latency}ms {self.bot.internal_emotes['outage']}**" # If the outage is over 400, mark the shard as fatal.
            elif latency > 300:
                latency = f"{self.bot.internal_emotes['outage']} {latency}ms"
            elif latency > 200:
                latency = f"🔴 {latency}ms"
            elif latency > 100:
                latency = f"🟡 {latency}ms"
            elif shard.is_closed(): # The shard is offline, therefore has no latency.
                latency = f"**{self.bot.internal_emotes['outage']} Offline.**"
            else:
                latency = f"🟢 {latency}"
            shards.append(f"Shard {i}: {guilds} guilds, {users} users, {latency}")
        em = discord.Embed(title="Shard Information", description="\n".join(shards),color=self.bot.main_color())
        await ctx.send(embed=em)
    
    @commands.is_owner()
    @commands.command(name="guild", brief="Shows advanced guild information",aliases=["guildinfo"])
    async def guild(self, ctx, id : discord.Guild = None):
        if id == None:
            id = ctx.guild
        em = discord.Embed(title="Guild Information", color=self.bot.main_color())
        em.add_field(name="Name", value=id.name)
        em.add_field(name="ID", value=id.id)
        em.add_field(name="Owner", value=id.owner)
        em.add_field(name="Owner ID", value=id.owner_id)
        em.add_field(name="Created", value=id.created_at.strftime("%a, %d %b %Y %I:%M %p"))
        em.add_field(name="Members", value=len(id.members))
        em.add_field(name="Text Channels", value=len(id.text_channels))
        em.add_field(name="Voice Channels", value=len(id.voice_channels))
        em.add_field(name="Roles", value=len(id.roles))
        em.add_field(name="Emojis", value=len(id.emojis))
        em.add_field(name="Verification Level", value=id.verification_level)
        em.add_field(name="Content Filter", value=id.explicit_content_filter)
        em.add_field(name="MFA Level", value=id.mfa_level)
        em.add_field(name="Large", value=id.large)
        em.add_field(name="Unavailable", value=id.unavailable)
        em.add_field(name="Shard ID", value=id.shard_id)
        em.add_field(name="Default Notifications", value=id.default_notifications)
        em.add_field(name="System Channel", value=id.system_channel)
        em.add_field(name="AFK Channel", value=id.afk_channel)
        em.add_field(name="AFK Timeout", value=id.afk_timeout)
        em.add_field(name="Icon URL", value=f"[Click Here]({id.icon})")
        em.add_field(name="Splash URL", value=f"[Click Here]({id.splash})")
        em.add_field(name="Banner URL", value=f"[Click Here]({id.banner})")
        await ctx.send(embed=em)
        
    @commands.is_owner()
    @commands.group(name="badge", brief="Badge commands", invoke_without_command=True)
    async def badge(self, ctx):
        await self.bot.invoke(ctx, "help badge")
        
    @commands.is_owner()
    @badge.command(name="add", brief="Adds a badge to a user")
    async def badge_add(self, ctx, user : discord.Member, badge : str):
        if badge.lower() in self.bot.badges.keys():
            try:
                if not badge.lower() in self.bot.db.users.find_one({"id": user.id})["badges"]:
                    self.bot.db.users.update_one({"id": user.id}, {"$push": {"badges": badge.lower()}},upsert=True)
                    await ctx.send(f"Added {badge} to {user}'s badge collection.")
                else:
                    await ctx.send(f"{user} already has {badge}!")
            except TypeError:
                self.bot.db.users.update_one({"id": user.id}, {"$push": {"badges": badge.lower()}},upsert=True)
                await ctx.send(f"Added {badge} to {user}'s badge collection.")
            except Exception as e:
                raise e
        else:
            await ctx.send("That isn't a valid badge!")
            
    @commands.is_owner()
    @badge.command(name="remove", brief="Removes a badge from a user")
    async def badge_remove(self, ctx, user : discord.Member, badge : str):
        if badge.lower() in self.bot.badges.keys():
            if badge.lower() in self.bot.db.users.find_one({"id": user.id})["badges"]:
                self.bot.db.users.update_one({"id": user.id}, {"$pull": {"badges": badge.lower()}},upsert=True)
                await ctx.send(f"Removed {badge} from {user}'s badge collection.")
            else:
                await ctx.send(f"{user} doesn't have {badge}!")
        else:
            await ctx.send("That isn't a valid badge!")
            
    @commands.is_owner()
    @badge.command(name="list", brief="Lists all badges a user has")
    async def badge_list(self, ctx, user : discord.Member):
        badges = self.bot.db.users.find_one({"id": user.id})["badges"]
        if len(badges) == 0:
            await ctx.send(f"{user} doesn't have any badges!")
        else:
            em = discord.Embed(title=f"{user}'s Badges", color=self.bot.main_color())
            for x in badges:
                em.add_field(name=f'{self.bot.badges[x]["icon"]} {self.bot.badges[x]["name"]}', value=self.bot.badges[x]["description"])
            await ctx.send(embed=em)
            
    @commands.is_owner()
    @badge.command(name="all", brief="Lists all badges")
    async def badge_all(self, ctx):
        em = discord.Embed(title="All Loaded Badges", color=self.bot.main_color())
        #em.description = ", ".join([self.bot.badges[x]["name"] for x in self.bot.badges.keys()])
        for x in self.bot.badges:
            em.add_field(name=f'{self.bot.badges[x]["icon"]} {self.bot.badges[x]["name"]}', value=self.bot.badges[x]["description"])
        await ctx.send(embed=em)
    
    @commands.is_owner()
    @commands.command(brief="Shows the code for a command while redacting sensitive information.")
    async def source(self,ctx, *, command : str):
        """Shows you the code for a command."""
        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.reply('Could not find command.')
        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        if not lines:
            return await ctx.reply('```py\nCould not retrieve source.\n```')
        # Strip any values that are defined in the ENV file
        env = os.environ
        for line in lines:
            for key in env:
                if key in line:
                    lines[lines.index(line)] = line.replace(env[key], f"{{{key}}}")
        # Backslash any backticks
        hasSuppressedMarkdown = False
        for line in lines:
            if "`" in line:
                lines[lines.index(line)] = line.replace("`", "\`")
                hasSuppressedMarkdown = True
        
        # And now embedify
        em = discord.Embed(title=f"Source for {command}", color=self.bot.main_color())
        if hasSuppressedMarkdown:
            em.set_footer(text="Makdown has been suppressed in this message. This is because the source code contains a backtick (`).")
            
        formatted = f'```py\n{"":>4}\n{"":>4}{"".join(lines)}\n{"":>4}\n```'
        
        if len(formatted) > 2000:
            # If it's too long, send it as a file
            with open("source.txt", "w") as f:
                f.write(formatted)
            await ctx.reply(file=discord.File("source.txt"))
            os.remove("source.txt")
            formatted = "Provided as a file. (Too long to embed)"
            
        await ctx.reply(content=formatted,embed=em)
        #await ctx.send(f'```py\n{"":>4}\n{"":>4}{"".join(lines)}\n{"":>4}\n```')
        
    @commands.is_owner()
    @commands.command(brief="Sends the crash log of an error")
    async def log(self, ctx, error_id):
        # Check if the error exists by checking for the error ID
        # We need to check both the database and ``error_dump.json`` in the event of a DB outage
        # error_dump SHOULDN'T exist unless there's a DB outage, but we'll check it anyway
        if self.bot.db.error_dumps.find_one({"id": error_id}) or os.path.exists("error_dump.json"):
            error = None
            # Check the DB first
            if self.bot.db.error_dumps.find_one({"id": error_id}):
                error = self.bot.db.error_dumps.find_one({"id": error_id})
            else:
                # Check the JSON file
                with open("error_dump.json", "r") as f:
                    errors = json.load(f)
                if error_id in errors.keys():
                    error = errors[error_id]
                else:
                    return await ctx.reply("That error doesn't exist!")
            if error:
                # The error exists, so send it.
                # As explained in ``index.py``, dumps have a lot of information. We'll send it all.
                # We'll send the traceback as a file, and the rest as an embed.
                em = discord.Embed(title=f"Error {error_id}", description=f"Command: ``{error['command']}``\nTraceback Provided in the file.", color=self.bot.main_color())
                em.add_field(name="ID", value=error["id"])
                em.add_field(name="User", value=f'{error["user"]["name"]} ({error["user"]["id"]})')
                try:
                    em.add_field(name="Guild", value=f'{error["guild"]["name"]} ({error["guild"]["id"]})')
                    # "Jump to message" link, only usable in guilds
                    em.add_field(name="Message", value=f'[Jump to message]({error["link"]})')
                except: # This is a DM
                    em.add_field(name="Guild", value=f'N/A (Triggered in Direct Messages)')
                
                #em.add_field(name="Error Caused In File", value=error["point"]) # Broken
                em.add_field(name="Error Caused In Fine", value="Deprecated")

                # We need to add a condition for Locale, as if its "fallback" the following code will error
                if error["locale"] != "fallback":
                    # As always, grab the flag and language name from the locale
                    with open(f"./locale/{error['locale']}.json", "r") as f:
                        locale = json.load(f)
                    em.add_field(name="Locale Set", value=f'{locale["meta"]["flag"]} {locale["meta"]["english_name"]}')
                else:
                    em.add_field(name="Locale Set", value="N/A (Not Provided in Error Dump)")
                    
                # Provide CPU, RAM, DISK, UPTIME and OS information as provided in the "sysinfo" section
                em.add_field(name="CPU", value=error["sysinfo"]["cpu"])
                em.add_field(name="RAM", value=error["sysinfo"]["ram"])
                em.add_field(name="Disk", value=error["sysinfo"]["disk"])
                em.add_field(name="Uptime", value=error["sysinfo"]["uptime"])
                em.add_field(name="OS", value=error["sysinfo"]["os"])
                em.add_field(name="Python Version", value=error["sysinfo"]["python"])
                
                # Send all the library versions as one field
                lib_versions = ""
                for lib in error["sysinfo"]["lib_versions"]:
                    # We'll use the library name as the key, and the version as the value
                    lib_versions += f'{lib}: {error["sysinfo"]["lib_versions"][lib]}\n'
                    
                em.add_field(name="Library Versions", value=lib_versions)
                
                # And lastly, send the traceback as a file
                with open("traceback.txt", "w") as f:
                    f.write(error["traceback"])
                await ctx.reply(file=discord.File("traceback.txt"), embed=em)
                os.remove("traceback.txt")
                
        else:
             await ctx.send("That error doesn't exist!")
        
    @commands.is_owner()
    @commands.command(brief="Triggers an error.")
    async def error(self, ctx):
        # We need to trigger an error that won't stop the cog from loading
        # We'll use a simple division by zero error
        1 / 0
        
    @commands.is_owner()
    @commands.command(brief="Tests image generation")
    async def testimage(self, ctx, function):
        # Very messy but its temporary
        # Get a timestamp to test latency
        before = time.time()
        
        # Generate the image
        if function == "welcome":
            image = await image_generation.generate_welcome_image(ctx.author, ctx.guild, None)
        elif function == "welcome_background": 
            image = await image_generation.generate_welcome_image(ctx.author, ctx.guild, "https://media.discordapp.net/attachments/747145826765242459/1061005236828909618/a82080c2-895d-4ce8-bb5b-8a7274881cd7.jpg")
        elif function == "leave":
            image = await image_generation.generate_leave_image(ctx.author, ctx.guild, "https://media.discordapp.net/attachments/747145826765242459/1061005236828909618/a82080c2-895d-4ce8-bb5b-8a7274881cd7.jpg")
        # Get the time after the image is generated
        after = time.time()
            
        # Send the image, and the time it took to generate it
        await ctx.reply(file=discord.File(image), content=f"Generated in {round((after - before) * 1000)}ms")
        # Delete the file
        os.remove(image)
    
async def setup(bot):
    await bot.add_cog(AdminTools(bot))