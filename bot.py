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

@bot.tree.command(name="teamshuffle", description="Suskirsto žaidėjus į komandas")
@app_commands.describe(
    voice_channel="Balso kanalas iš kurio paimti žaidėjus",
    komandu_skaicius="Kiek komandų sukurti (palik tuščią, jei nori nurodyti žaidėjų skaičių komandoje)",
    zaideju_vienoje_komandoje="Kiek žaidėjų komandoje (palik tuščią, jei nori nurodyti komandų skaičių)"
)
async def teamshuffle(
    interaction: discord.Interaction,
    voice_channel: discord.VoiceChannel,
    komandu_skaicius: int = None,
    zaideju_vienoje_komandoje: int = None
):
    # Validacija - turi būti nurodytas tik vienas parametras
    if komandu_skaicius is not None and zaideju_vienoje_komandoje is not None:
        await interaction.response.send_message(
            "❌ Nurodykite tik komandų skaičių ARBA žaidėjų skaičių komandoje, ne abu!",
            ephemeral=True
        )
        return
    
    if komandu_skaicius is None and zaideju_vienoje_komandoje is None:
        await interaction.response.send_message(
            "❌ Nurodykite komandų skaičių ARBA žaidėjų skaičių komandoje!",
            ephemeral=True
        )
        return

    # Gauname visus narius balso kanale (išskyrus botus)
    members = [member for member in voice_channel.members if not member.bot]
    
    # Validacijos
    if len(members) == 0:
        await interaction.response.send_message(
            f"❌ Balso kanale **{voice_channel.name}** nėra žaidėjų!",
            ephemeral=True
        )
        return

    # Maišome žaidėjus
    random.shuffle(members)
    
    if komandu_skaicius is not None:
        # Skirstome pagal komandų skaičių
        if komandu_skaicius < 1:
            await interaction.response.send_message("❌ Turi būti bent 1 komanda!", ephemeral=True)
            return
            
        if komandu_skaicius > len(members):
            await interaction.response.send_message(
                f"❌ Negalima sukurti {komandu_skaicius} komandų - kanale tik {len(members)} žaidėjų!",
                ephemeral=True
            )
            return

        team_size = len(members) // komandu_skaicius
        remainder = len(members) % komandu_skaicius
        
        teams = []
        start = 0
        for i in range(komandu_skaicius):
            current_team_size = team_size + (1 if i < remainder else 0)
            team = members[start:start + current_team_size]
            teams.append(team)
            start += current_team_size
        
        result = f"**{len(members)} žaidėjų iš {voice_channel.mention} | {komandu_skaicius} komandos**\n\n"
        
    else:
        # Skirstome pagal žaidėjų skaičių komandoje (esama logika)
        if zaideju_vienoje_komandoje < 1:
            await interaction.response.send_message("❌ Komandoje turi būti bent 1 žaidėjas!", ephemeral=True)
            return
            
        if zaideju_vienoje_komandoje > len(members):
            await interaction.response.send_message(
                f"❌ Negalima sudaryti komandų po {zaideju_vienoje_komandoje} žaidėjų - kanale tik {len(members)} žaidėjų!",
                ephemeral=True
            )
            return

        teams = []
        for i in range(0, len(members), zaideju_vienoje_komandoje):
            team = members[i:i + zaideju_vienoje_komandoje]
            teams.append(team)
        
        result = f"**{len(members)} žaidėjų iš {voice_channel.mention} | Komandos po {zaideju_vienoje_komandoje} žaidėjus**\n\n"
    
    # Formatuojame rezultatą
    for idx, team in enumerate(teams, 1):
        team_list = "\n".join(f"> {member.mention}" for member in team)
        result += f"**Komanda #{idx}** ({len(team)} žaidėjų)\n{team_list}\n\n"
    
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