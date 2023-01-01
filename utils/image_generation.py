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
    # # Load the background from URL
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(background) as resp:
    #         if resp.status != 200:
    #             return "Failed to get background image."
    #         data = io.BytesIO(await resp.read())
    #         with Image.open(data) as img:
    #             # Open the background
    #             background = img
    #             # Convert to RGBA
    #             background = background.convert("RGBA")
    #             # Resize the background to 1280x720
    #             background = background.resize((1280, 720), Image.ANTIALIAS)
    #             # Get the fonts
    #             font = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 50)
    #             font_small = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 30)
    #             font_smaller = ImageFont.truetype("utils/fonts/Roboto-Reguar.ttf", 20)
    #             # Get a drawing context
    #             draw = ImageDraw.Draw(background)
    #             # Draw the welcome text
    #             draw.text((650, 150), "Welcome to", (255, 255, 255), font=font)
    #             draw.text((650, 250), guild.name, (255, 255, 255), font=font)
    #             # Draw the user's name
    #             draw.text((650, 350), user.name, (255, 255, 255), font=font_small)
    #             # Draw the user's discriminator
    #             draw.text((650, 400), "#" + user.discriminator, (255, 255, 255), font=font_smaller)
    #             # Draw the user's avatar
    #             avatar = Image.open(io.BytesIO(await user.avatar_url.read()))
    #             avatar = avatar.resize((250, 250), Image.ANTIALIAS)
    #             background.paste(avatar, (350, 200), avatar)
    #             # Save the image, suffix with UserID + Timestamp + GuildID
    #             background.save(f"images/{user.id}-{int(datetime.datetime.now().timestamp())}-{guild.id}.png")
    #             return f"images/{user.id}-{int(datetime.datetime.now().timestamp())}-{guild.id}.png"
    # Temporarily use a static image instead of using background
    background = Image.open("assets/placeholder.jpg")
    # Convert to RGBA
    background = background.convert("RGBA")
    # Resize the background to 640x360 (16:9)
    # Original size: 1280x720
    background = background.resize((640, 360), Image.ANTIALIAS)
    # Get the fonts
    font = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 35)
    font_bigger = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 45)
    font_small = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 25)
    font_smaller = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 20)
    # Get a drawing context
    draw = ImageDraw.Draw(background)
    
    # Draw a text shadow for all the text, so it's easier to read
    draw.text((240, 100), "Welcome to", (0, 0, 0), font=font_bigger)
    draw.text((256, 140), guild.name, (0, 0, 0), font=font)
    draw.text((250, 175), user.name, (0, 0, 0), font=font_small)
    draw.text((250, 200), "#" + user.discriminator, (0, 0, 0), font=font_smaller)
    
    # Draw the welcome text
    draw.text((241, 100), "Welcome to", (255, 255, 255), font=font_bigger)
    draw.text((257, 140), guild.name, (255, 255, 255), font=font)
    # Draw the user's name
    draw.text((251, 175), user.name, (255, 255, 255), font=font_small)
    # Draw the user's discriminator
    draw.text((251, 200), "#" + user.discriminator, (255, 255, 255), font=font_smaller)
    
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
    background.paste(avatar, (75, 100), avatar)
    
    # Save the image
    # The "image ID" will be the UserID + Timestamp + GuildID encoded to base64
    # This will be generated and used as a file name
    image_id = base64.b64encode(f"{user.id}-{int(datetime.datetime.now().timestamp())}-{guild.id}".encode("utf-8"))
    
    # Then remove all characters that NFTS and ext4 don't like
    # No idea what OSX uses as a file system, but I'm sure it's similar
    image_id = image_id.decode("utf-8").replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")

    # Compress the image to JPEG and save it
    background = background.convert("RGB")
    
    background.save(f"temp/welcome-{image_id}.jpg", optimize=True, progressive=True, format="JPEG")
    return f"temp/welcome-{image_id}.jpg"


# Leave Image Generation #
# This is the same as the welcome image generation, but with different text
async def generate_leave_image(user, guild):
    # Temporarily use a static image instead of using background
    background = Image.open("assets/placeholder.jpg")
    # Convert to RGBA
    background = background.convert("RGBA")
    # Resize the background to 640x360 (16:9)
    background = background.resize((640, 360), Image.ANTIALIAS)
    # Get the fonts
    font = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 35)
    font_bigger = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 45)
    font_small = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 25)
    font_smaller = ImageFont.truetype("utils/fonts/Roboto-Regular.ttf", 20)
    # Get a drawing context
    draw = ImageDraw.Draw(background)
    
    # Draw a text shadow for all the text, so it's easier to read
    draw.text((240, 100), "Goodbye", (0, 0, 0), font=font_bigger)
    draw.text((256, 150), user.name, (0, 0, 0), font=font_smaller)
    draw.text((250, 175), "#" + user.discriminator, (0, 0, 0), font=font_smaller)
    # draw.text((256, 200), "from", (0, 0, 0), font=font_small)
    # draw.text((256, 225), guild.name, (0, 0, 0), font=font)
    
    # Draw the welcome text
    draw.text((241, 100), "Goodbye", (255, 255, 255), font=font_bigger)
    draw.text((257, 150), user.name, (255, 255, 255), font=font_smaller)
    # Draw the user's name
    draw.text((251, 175), "#" + user.discriminator, (255, 255, 255), font=font_smaller)
    # draw.text((257, 200), "from", (255, 255, 255), font=font_small)
    # draw.text((257, 225), guild.name, (255, 255, 255), font=font)
    
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
    background.paste(avatar, (75, 100), avatar)
    
    # Save the image
    # The "image ID" will be the UserID + Timestamp + GuildID encoded to base64
    # This will be generated and used as a file name
    image_id = base64.b64encode(f"{user.id}-{int(datetime.datetime.now().timestamp())}-{guild.id}".encode("utf-8"))
    
    # Then remove all characters that NFTS and ext4 don't like
    # No idea what OSX uses as a file system, but I'm sure it's similar
    image_id = image_id.decode("utf-8").replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
    
    # Compress the image to JPEG and save it
    background = background.convert("RGB")
    background.save(f"temp/leave-{image_id}.jpg", optimize=True, progressive=True, format="JPEG")
    return f"temp/leave-{image_id}.jpg"