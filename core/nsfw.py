# God left us a long time ago, but we still have to deal with his mess.

import asyncio
import json
import os
import random

import aiohttp
import discord
from discord.ext import commands

banned_tags = [ # Tags that will get me banned from Discord if the bot is reported.. So hide them in all queries #
    "age_difference",
    "rape",
    "cub",
    "lolicon",
    "loli"
]

unsupported_formats = [
    "swf",
    "webm",
    "mp4"
]


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.is_nsfw()
    @commands.command(brief="Grabs a random image with the given tags from e621",aliases=["e6"])
    async def e621(self, ctx, *tags):
        if "frostbyte" in tags and "rating:e" in tags:
            # Award the "no horny" badge
            badges = ctx.bot.db.users.find_one({"id": ctx.author.id})["badges"]
            # If the user already has the badge, do nothing #
            if "nohorny" not in badges:
                badges.append("nohorny")
                ctx.bot.db.users.update_one({"id": ctx.author.id}, {"$set": {"badges": badges}})
                await ctx.author.send("You have been awarded the **No Horny** badge.\nFucking perv.")
            
            
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://e621.net/posts.json?tags={'+'.join(tags)}&login={os.getenv('E621_USERNAME')}&api_key={os.getenv('E621_KEY')}&limit=300",headers={"User-Agent": os.getenv("USER_AGENT"),"Content-Type": "application/json"}) as r:
                if r.status == 200:
                    retries = 0
                    data = await r.json()
                    chosen = random.choice(data["posts"])
                    # I'm gonna be honest, only now did I realise this will only reroll judging on the first picked post. Whoops. #
                    while chosen["file"]["ext"] in unsupported_formats or chosen["flags"]["deleted"] == True or chosen["flags"]["pending"] == True or chosen["flags"]["flagged"] == True or chosen["score"]["total"] < 0: # This takes up my 1440p monitor 
                        if retries > 10:
                            await ctx.send_locale("NSFWNoUsableResults")
                            return
                        chosen = random.choice(data["posts"])
                        retries += 1
                    # Check for banned tags #
                    for tag in chosen["tags"]["general"]:
                        if tag in banned_tags:
                            retries += 1
                            print("Rerolling, reason: " + tag)
                            # Then redo the checks. #
                            while chosen["file"]["ext"] in unsupported_formats or chosen["flags"]["deleted"] == True or chosen["flags"]["pending"] == True or chosen["flags"]["flagged"] == True or chosen["score"]["total"] < 0: # This takes up my 1440p monitor 
                                if retries > 10:
                                    await ctx.send_locale("NSFWNoUsableResults")
                                    return
                                chosen = random.choice(data["posts"])
                                retries += 1
                    # Now scream. #
                    if len(data) > 0:
                        try:
                            em = discord.Embed(description=f"[{chosen['description'] if chosen['description'] else 'No description available'}]({chosen['sources'][0]})", color=self.bot.main_color(),url=chosen['sources'][0])
                        except:
                            em = discord.Embed(description=f"{chosen['description'] if chosen['description'] else 'No description available'}", color=self.bot.main_color())
                        em.set_image(url=chosen["file"]["url"])
                        em.set_footer(text=f"Score: {chosen['score']['total']} | Artist: {chosen['tags']['artist'][0]} | Rating: {chosen['rating']}")
                        await ctx.send(embed=em)
                    else:
                        await ctx.send_locale(message="NSFWNoResults")
                else:
                    await ctx.send_locale(message="NSFWError")

        
async def setup(bot):
    await bot.add_cog(NSFW(bot))