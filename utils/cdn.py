# Manages posting and retrieving files from the CDN

import os
import aiohttp
import dotenv 
dotenv.load_dotenv()

async def post_file(file, name=None):
    async with aiohttp.ClientSession() as session:
        # Post the file to the CDN
        # If the bot is running on Staging, use localhost:6984
        # Otherwise, use frostbyte.jackelope.gay/cdn
        async with session.post(f"http://localhost:6984/cdn" if os.getenv("DEPLOYED") == "STAGING" else "https://frostbyte.jackelope.gay/cdn/",
                                # The file needs to be the body of the request
                                data=file,
                                headers={"file": name}) as resp:
            # If the status code isn't 200, return None
            if resp.status != 200:
                return None
            # Otherwise, return the response
            return await resp.json()
        
async def get_file(file_id):
    async with aiohttp.ClientSession() as session:
        # Get the file from the CDN
        async with session.get(f"http://localhost:6984/cdn/{file_id}" if os.getenv("DEPLOYED") == "STAGING" else f"https://frostbyte.jackelope.gay/cdn/{file_id}") as resp:
            # If the status code isn't 200, return None
            if resp.status != 200:
                return None
            # Otherwise, return the response
            return await resp.read()