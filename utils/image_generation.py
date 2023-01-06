# utils/image_generation.py
# Handles generating images for UserInfo, and other image related tasks
# All using PIL

import os
import random
import PIL
import aiohttp
import io
import base64

from PIL import Image, ImageDraw, ImageFont
import datetime


# Welcome Image generation
async def generate_welcome_image(user, guild, background):
    # Get the background from the URL
    async with aiohttp.ClientSession() as session:
        async with session.get(background) as r:
            if r.status == 200:
                js = await r.read()
                background = Image.open(io.BytesIO(js))
            else:
                # Temporarily use a static image instead of using background
                background = Image.open("assets/placeholder.jpg")
    # Convert to RGBA
    background = background.convert("RGBA")
    # Resize the background to 640x360 (16:9)
    # Original size: 1280x720
    #background = background.resize((640, 360), Image.ANTIALIAS)
    # If the background is smaller than 640x360, resize it to 640x360
    # Otherwise, crop it to 640x360
    if background.size[0] < 640 or background.size[1] < 360:
        background = background.resize((640, 360), Image.ANTIALIAS)
    else:
        background = background.crop((0, 0, 640, 360))
    
    
    # Get the fonts
    font = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 35)
    font_bigger = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 45)
    font_small = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 25)
    font_smaller = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 20)
    # Get a drawing context
    draw = ImageDraw.Draw(background)
    
    # Draw a text shadow for all the text, so it's easier to read
    draw.text((220, 100), "Welcome to", (0, 0, 0), font=font_bigger)
    draw.text((236, 140), guild.name, (0, 0, 0), font=font)
    draw.text((230, 175), user.name, (0, 0, 0), font=font_small)
    draw.text((230, 200), "#" + user.discriminator, (0, 0, 0), font=font_smaller)
    
    # Draw the welcome text
    draw.text((221, 100), "Welcome to", (255, 255, 255), font=font_bigger)
    draw.text((237, 140), guild.name, (255, 255, 255), font=font)
    # Draw the user's name
    draw.text((231, 175), user.name, (255, 255, 255), font=font_small)
    # Draw the user's discriminator
    draw.text((231, 200), "#" + user.discriminator, (255, 255, 255), font=font_smaller)
    
    # Draw the user's avatar
    avatar = Image.open(io.BytesIO(await user.avatar.read())).convert("RGBA")
    avatar = avatar.resize((150, 150), Image.ANTIALIAS)
    
    # Make the avatar a circle
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar.size, fill=255)
    mask = mask.resize(avatar.size, Image.ANTIALIAS)
    avatar.putalpha(mask)
    
    # Then paste it onto the background
    background.paste(avatar, (55, 100), avatar)
    
    # Save the image
    # The "image ID" will be the UserID + Timestamp + GuildID encoded to base64
    # This will be generated and used as a file name
    image_id = base64.b64encode(f"{user.id}{int(datetime.datetime.now().timestamp())}{guild.id}".encode("utf-8"))
    
    # Then remove all characters that NFTS and ext4 don't like
    # No idea what OSX uses as a file system, but I'm sure it's similar
    image_id = image_id.decode("utf-8").replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")

    # Compress the image to JPEG and save it
    #background = background.convert("RGB")
    
    background.save(f"temp/welcome-{image_id}.png", optimize=True, progressive=True, format="PNG")
    return f"temp/welcome-{image_id}.png"


# Leave Image Generation #
# This is the same as the welcome image generation, but with different text
async def generate_leave_image(user, guild, background):
    # Get the background from the URL
    async with aiohttp.ClientSession() as session:
        async with session.get(background) as r:
            if r.status == 200:
                js = await r.read()
                background = Image.open(io.BytesIO(js))
            else:
                # Temporarily use a static image instead of using background
                background = Image.open("assets/placeholder.jpg")
    # Convert to RGBA
    background = background.convert("RGBA")
    # Resize the background to 640x360 (16:9)
    # Original size: 1280x720
    #background = background.resize((640, 360), Image.ANTIALIAS)
    # If the background is smaller than 640x360, resize it to 640x360
    # Otherwise, crop it to 640x360
    if background.size[0] < 640 or background.size[1] < 360:
        background = background.resize((640, 360), Image.ANTIALIAS)
    else:
        background = background.crop((0, 0, 640, 360))
    
    
    # Get the fonts
    font = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 35)
    font_bigger = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 45)
    font_small = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 25)
    font_smaller = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 20)
    # Get a drawing context
    draw = ImageDraw.Draw(background)
    
    # Draw a text shadow for all the text, so it's easier to read
    draw.text((220, 130), "Goodbye", (0, 0, 0), font=font_bigger)
    draw.text((230, 190), user.name, (0, 0, 0), font=font_small)
    draw.text((230, 220), "#" + user.discriminator, (0, 0, 0), font=font_smaller)
    
    # Draw the welcome text
    draw.text((221, 130), "Goodbye", (255, 255, 255), font=font_bigger)
    draw.text((231, 190), user.name, (255, 255, 255), font=font_small)
    # Draw the user's discriminator
    draw.text((231, 220), "#" + user.discriminator, (255, 255, 255), font=font_smaller)
    
    # Draw the user's avatar
    avatar = Image.open(io.BytesIO(await user.avatar.read())).convert("RGBA")
    avatar = avatar.resize((150, 150), Image.ANTIALIAS)
    
    # Make the avatar a circle
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar.size, fill=255)
    mask = mask.resize(avatar.size, Image.ANTIALIAS)
    avatar.putalpha(mask)
    
    # Then paste it onto the background
    background.paste(avatar, (55, 100), avatar)
    
    # Save the image
    # The "image ID" will be the UserID + Timestamp + GuildID encoded to base64
    # This will be generated and used as a file name
    image_id = base64.b64encode(f"{user.id}{int(datetime.datetime.now().timestamp())}{guild.id}".encode("utf-8"))
    
    # Then remove all characters that NFTS and ext4 don't like
    # No idea what OSX uses as a file system, but I'm sure it's similar
    image_id = image_id.decode("utf-8").replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")

    # Compress the image to JPEG and save it
    #background = background.convert("RGB")
    
    background.save(f"temp/leave-{image_id}.png", optimize=True, progressive=True, format="PNG")
    return f"temp/leave-{image_id}.png"
