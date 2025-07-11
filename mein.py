import discord
from discord.ext import commands
import random
import math
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # nutné pro práci s rolemi
bot = commands.Bot(command_prefix="!", intents=intents)

countries_capitals = {
    "Česko": "Praha", "Francie": "Paříž", "USA": "Washington, D.C.", "Vietnam": "Hanoj",
    "Angola": "Luanda", "Belgie": "Brusel", "Dánsko": "Kodaň", "Japonsko": "Tokio"
    # můžeš rozšířit celý svůj seznam
}

# Stav hráče – {uživatel_id: {"score": X, "role": "Název ligy"}}
player_state = {}

ligy = [
    (10000, "Legendární liga"),
    (5000, "Diamantová liga"),
    (2500, "Zlatá liga"),
    (1000, "Stříbrná liga"),
    (0, "Bronzová liga")
]

def urci_ligu(score):
    for minimum, role in ligy:
        if score >= minimum:
            return role
    return "Bronzová liga"

async def aktualizuj_roli(member, score):
    nova_role_jmeno = urci_ligu(score)
    guild = member.guild
    nova_role = discord.utils.get(guild.roles, name=nova_role_jmeno)

    if nova_role is None:
        return  # role neexistuje

    # Odeber staré ligy
    stare_role = [discord.utils.get(guild.roles, name=r[1]) for r in ligy if discord.utils.get(guild.roles, name=r[1]) in member.roles]
    for sr in stare_role:
        await member.remove_roles(sr)

    await member.add_roles(nova_role)

@bot.command()
async def hlavni_mesto(ctx):
    x = 4

    country = random.choice(list(countries_capitals.keys()))
    correct = countries_capitals[country]
    wrongs = random.sample(list(set(countries_capitals.values()) - {correct}), x - 1)
    options = wrongs + [correct]
    random.shuffle(options)
    numbered = {i + 1: options[i] for i in range(x)}

    # Ulož otázku
    stav = player_state.get(ctx.author.id, {"score": 0})
    stav["country"] = country
    stav["correct"] = correct
    stav["options"] = numbered
    player_state[ctx.author.id] = stav

    text = f"Jaké je hlavní město **{country}**?\n"
    for i, cap in numbered.items():
        text += f"{i}. {cap}\n"
    text += "Odpověz pomocí !odpoved <číslo>"
    await ctx.send(text)

@bot.command()
async def odpoved(ctx, cislo: int):
    stav = player_state.get(ctx.author.id)
    if not stav or "options" not in stav:
        await ctx.send("Nejdřív spusť hru pomocí !hlavni_mesto.")
        return

    moznosti = stav["options"]
    if cislo not in moznosti:
        await ctx.send("Zadané číslo není mezi možnostmi.")
        return

    vybrana = moznosti[cislo]
    correct = stav["correct"]
    score = stav.get("score", 0)
    previous_score = score

    if vybrana == correct:
        score += 100
        await ctx.send(f"✅ Správně! {correct} je hlavní město {stav['country']}. Máš teď {score} bodů.")
    else:
        penalty = math.ceil(score / 20)
        score = max(0, score - penalty)
        await ctx.send(f"❌ Špatně! Správná odpověď byla **{correct}**. Ztratil(a) jsi {penalty} bodů. Máš teď {score} bodů.")

    # Přiřaď roli podle skóre
    member = ctx.author
    await aktualizuj_roli(member, score)

    # Ulož nový stav
    player_state[ctx.author.id] = {"score": score}

@bot.command()
async def skore(ctx):
    stav = player_state.get(ctx.author.id, {"score": 0})
    score = stav.get("score", 0)
    liga = urci_ligu(score)

    dalsi_liga = None
    for minbody, jmeno in ligy:
        if score < minbody:
            dalsi_liga = (minbody, jmeno)
            break

    text = f"🎯 Tvoje skóre: **{score}**\n🏅 Tvoje liga: **{liga}**\n"
    if dalsi_liga:
        text += f"➡️ Chybí ti ještě {dalsi_liga[0] - score} bodů do ligy **{dalsi_liga[1]}**!"
    else:
        text += "🥳 Dosáhl(a) jsi nejvyšší ligy! Gratulujeme!"

    await ctx.send(text)

# Spusť bota
bot.run("MTM5MzE0MjA5ODYwNTM3NTU3OA.G67drJ.Pwx2p0YWA6gbhN9CsfL_eXxXHkIeR0qgsv8tpU")
