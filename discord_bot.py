import discord
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import linkify_lib
import asyncio

load_dotenv() # Load all the variables from the .env file
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="linkify", description="Linkify a student")
async def linkify(ctx, login: str):
    await ctx.defer() # Defer the response to avoid the "This interaction failed" error
    image = await asyncio.to_thread(linkify_lib.linkify_user, login) # Run the blocking function in a separate thread
    if image is None:
        await ctx.respond("Couldn't find that login.")
    else:
        # Save the PIL image to a BytesIO object and send it
        with BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0) # Go to the start of the BytesIO object
            await ctx.respond(f"Here's a linkified image of {login}!",file=discord.File(fp=image_binary, filename=f"{login}_link.png"))


bot.run(os.getenv('DISCORD_BOT_TOKEN')) # Run the bot with the token
