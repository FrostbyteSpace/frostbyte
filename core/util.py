import aiohttp
import aiohttp
import asyncio
import discord
from discord.ext import commands
import os

pronoun = {
    "unspecified": "Unspecified",
    "avoid": "Avoid using pronouns, use my name.",
    "any": "Any pronouns",
    "hh": "he/him",
    "hs": "he/she",
    "ht": "he/they",
    "shh": "she/he",
    "sh": "she/her",
    "st": "she/they",
    "th": "they/he",
    "ts": "they/she",
    "tt": "they/them",
    "other": "Other",
    "other_ask": "Other, ask me!"
}

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(alias=["av", "pfp"])
    async def avatar(self, ctx, member: discord.Member = None):
        """Get a user's avatar"""
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=await ctx.get_locale(message="AvatarTitle",username=member.name), color=member.color)
        embed.set_image(url=member.avatar)
        await ctx.send(embed=embed)
        
    @commands.command(aliases=["ui"])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get a user's info"""
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=await ctx.get_locale(message="UserInfoTitle",username=member.name), color=self.bot.main_color())
        embed.add_field(name="ID", value=member.id,inline=False)
        embed.add_field(name=await ctx.get_locale(message="UserInfoJoined"), value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name=await ctx.get_locale(message="UserInfoRegistered"), value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name=await ctx.get_locale(message="UserInfoRoles", count=str(len(member.roles) -1)), value=", ".join([role.mention for role in member.roles[1:]]), inline=False) # Remove @everyone 
        
        if member.nick:
            embed.add_field(name=await ctx.get_locale(message="UserInfoNickname"), value=member.display_name, inline=True)
            
        # Pronoun DB Integration
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pronoundb.org/api/v1/lookup?platform=discord&id={member.id}") as r:
                if r.status == 200:
                    js = await r.json()
                    embed.add_field(name=await ctx.get_locale(message="UserInfoPronouns"), value=pronoun[js["pronouns"]], inline=True) #TODO: Translate pronouns
                else:
                    embed.add_field(name=await ctx.get_locale(message="UserInfoPronouns"), value=await ctx.get_locale(message="UserInfoPronounsUnavailable"), inline=True)

        # Now this is a fancy one
        # Check for the user's "reputation" by checking other servers if they've been banned
        # Also add a stastical analysis of how many servers they've been banned from
        # and mutual server count
        mutual = 0
        banned = 0
        for guild in self.bot.guilds:
            if discord.utils.get(guild.members, id=member.id):
                mutual += 1
                # Do this in a try/except block because the bot might not have the ban permission
                try:
                    async for ban in guild.bans():
                        if ban.user.id == member.id:
                            banned += 1
                except:
                    pass # We don't have the ban permission, so we can't check
                
        # Then flatten it into a percentage
        # For mutual servers, get the percentage of the bot's guilds
        # For banned servers, get the percentage of the mutual servers
        mutual_percentage = round((mutual / len(self.bot.guilds)) * 100)
        banned_percentage = round((banned / mutual) * 100)
        
        # For the total "reputation", subtract BannedPercentage from 100
        total_percentage = 100 - banned_percentage
        
        # Eventually we'll add an upvote/downvote system, but for now, this is what we have
        
        embed.add_field(name=await ctx.get_locale(message="UserInfoReputation"), value=await ctx.get_locale(
            message="UserInfoReputationPercentage", 
            mutual=mutual, 
            banned=banned, 
            mutual_percentage=mutual_percentage, 
            banned_percentage=banned_percentage,
            total_percentage=total_percentage
            ), inline=False)
    
    
        # Temporary until we redo the badge system to generate an image
        fmt = []
        try:
            badges = self.bot.db.users.find_one({"id": member.id})["badges"]
            for x in badges:
                fmt.append(f"{self.bot.badges[x]['icon']} {self.bot.badges[x]['name']}\n - {self.bot.badges[x]['description']}")
            embed.add_field(name=await ctx.get_locale(message="UserInfoBadges"), value=("\n".join(fmt) if len(fmt) > 0 else await ctx.get_locale(message="UserInfoBadgesNone")), inline=False)
        except: # Not in the database, therefore add them
            self.bot.db.users.insert_one({"id": member.id, "badges": []})
            embed.add_field(name=await ctx.get_locale(message="UserInfoBadges"), value=await ctx.get_locale(message="UserInfoBadgesNone"), inline=False)
    
        embed.set_footer(text=await ctx.get_locale(message="UserInfoPronounsFooter"))
        embed.set_thumbnail(url=member.avatar)
        # TODO: Image generation for badges, pronouns and national flags
        user = await self.bot.fetch_user(member.id)
        embed.set_image(url=user.banner)
        
        await ctx.send(embed=embed)

        
        
async def setup(bot):
    await bot.add_cog(Utility(bot))