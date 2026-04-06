import discord
from discord.ext import commands
from discord import app_commands
from typing import List, Optional
import os

TOKEN = os.getenv("TOKEN")  # 👈 CAMBIO CLAVE

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def category_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    categories = [
        c for c in interaction.guild.channels
        if isinstance(c, discord.CategoryChannel)
        and current.lower() in c.name.lower()
    ]
    return [
        app_commands.Choice(name=c.name, value=c.name)
        for c in categories[:25]
    ]

@bot.tree.command(
    name="deletecategory",
    description="Elimina hasta 5 categorías y todos sus canales"
)
@app_commands.describe(
    categoria1="Primera categoría a eliminar",
    categoria2="Segunda categoría a eliminar",
    categoria3="Tercera categoría a eliminar",
    categoria4="Cuarta categoría a eliminar",
    categoria5="Quinta categoría a eliminar"
)
@app_commands.autocomplete(
    categoria1=category_autocomplete,
    categoria2=category_autocomplete,
    categoria3=category_autocomplete,
    categoria4=category_autocomplete,
    categoria5=category_autocomplete
)
@app_commands.checks.has_permissions(manage_channels=True)
async def deletecategory(
    interaction: discord.Interaction,
    categoria1: str,
    categoria2: Optional[str] = None,
    categoria3: Optional[str] = None,
    categoria4: Optional[str] = None,
    categoria5: Optional[str] = None
):
    await interaction.response.defer(ephemeral=True)

    nombres = [c for c in [categoria1, categoria2, categoria3, categoria4, categoria5] if c]
    eliminadas = []
    errores = []

    for nombre in nombres:
        category = discord.utils.find(
            lambda c, n=nombre: c.name.lower() == n.lower() and isinstance(c, discord.CategoryChannel),
            interaction.guild.channels
        )

        if category is None:
            errores.append(f"❌ No encontré la categoría **{nombre}**")
            continue

        canal_count = len(category.channels)
        fallo = False

        for channel in category.channels:
            try:
                await channel.delete(reason=f"Eliminado por {interaction.user}")
            except discord.Forbidden:
                errores.append(f"⚠️ Sin permiso para eliminar el canal **{channel.name}**")
                fallo = True
                break
            except discord.HTTPException as e:
                errores.append(f"⚠️ Error al eliminar **{channel.name}**: {e}")
                fallo = True
                break

        if fallo:
            continue

        try:
            await category.delete(reason=f"Eliminada por {interaction.user}")
            eliminadas.append(f"✅ **{nombre}** ({canal_count} canales)")
        except discord.Forbidden:
            errores.append(f"⚠️ Sin permiso para eliminar la categoría **{nombre}**")

    respuesta = ""
    if eliminadas:
        respuesta += "**Categorías eliminadas:**\n" + "\n".join(eliminadas) + "\n"
    if errores:
        respuesta += "\n**Errores:**\n" + "\n".join(errores)

    await interaction.followup.send(respuesta or "No se hizo nada.", ephemeral=True)

@deletecategory.error
async def deletecategory_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ No tienes permiso para usar este comando (necesitas **Manage Channels**).",
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar: {e}")

bot.run(TOKEN)