import os
import discord
import random
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Konfigūracija
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.tree.command(name="teamshuffle", description="Suskirsto balso kanalo žaidėjus į komandas pagal pasirinktą dydį")
@app_commands.describe(
    zaideju_vienoje_komandoje="Kiek žaidėjų turi būti vienoje komandoje",
    voice_channel="Balso kanalas iš kurio paimti žaidėjus"
)
async def teamshuffle(
    interaction: discord.Interaction,
    zaideju_vienoje_komandoje: int,
    voice_channel: discord.VoiceChannel
):
    # Gauname visus narius balso kanale (išskyrus botus)
    members = [member for member in voice_channel.members if not member.bot]
    
    # Validacijos
    if len(members) == 0:
        await interaction.response.send_message(
            f"❌ Balso kanale **{voice_channel.name}** nėra žaidėjų!",
            ephemeral=True
        )
        return
        
    if zaideju_vienoje_komandoje < 1:
        await interaction.response.send_message(
            "❌ Komandoje turi būti bent 1 žaidėjas!",
            ephemeral=True
        )
        return
        
    if zaideju_vienoje_komandoje > len(members):
        await interaction.response.send_message(
            f"❌ Negalima sudaryti komandų po {zaideju_vienoje_komandoje} žaidėjų - kanale tik {len(members)} žaidėjų!",
            ephemeral=True
        )
        return

    # Maišome žaidėjus
    random.shuffle(members)
    
    # Skirstome į komandas
    teams = []
    for i in range(0, len(members), zaideju_vienoje_komandoje):
        team = members[i:i + zaideju_vienoje_komandoje]
        teams.append(team)
    
    # Formatuojame rezultatą
    result = f"**{len(members)} žaidėjų iš {voice_channel.mention} | Komandos po {zaideju_vienoje_komandoje} žaidėjus**\n\n"
    for idx, team in enumerate(teams, 1):
        team_list = "\n".join(f"> {member.mention}" for member in team)
        result += f"**Komanda #{idx}**\n{team_list}\n\n"
    
    await interaction.response.send_message(result)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Botas prisijungė kaip {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="/teamshuffle")
    )

if __name__ == "__main__":
    bot.run(TOKEN)