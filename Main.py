import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

PEX_DEPEX_LOG_CHANNEL = 1504809976751722576
STRIKE_LOG_CHANNEL = 1504809979368968212
HELPER_ROLE_ID = 1504809811043160176
GANG_ROLE_ID = 1504809816974164099
INATTIVITA_CHANNEL = 1504809984041681106
RUOLO_INATTIVO = 1509254608327802911
RUOLO_RIENTRO = 1509254694722080929
ALT_CHANNEL = 1504809980409286777
REPORT_ROLE_ID = 1504809828822945813
REPORT_CHANNEL = 1504809986692218991
LISTA_MEMBRI_CHANNEL = 1504809951472914442
RUOLO_STRIKE1 = 1509288035676848290
RUOLO_STRIKE2 = 1509288084791885975


def is_helper():
    async def predicate(interaction: discord.Interaction) -> bool:
        role = discord.utils.get(interaction.user.roles, id=HELPER_ROLE_ID)
        if role is None:
            raise app_commands.CheckFailure("Non hai il ruolo necessario per usare questo comando!")
        return True
    return app_commands.check(predicate)


def is_gang():
    async def predicate(interaction: discord.Interaction) -> bool:
        role = discord.utils.get(interaction.user.roles, id=GANG_ROLE_ID)
        if role is None:
            raise app_commands.CheckFailure("Non hai il ruolo necessario per usare questo comando!")
        return True
    return app_commands.check(predicate)


def is_report_role():
    async def predicate(interaction: discord.Interaction) -> bool:
        role = discord.utils.get(interaction.user.roles, id=REPORT_ROLE_ID)
        if role is None:
            raise app_commands.CheckFailure("Non hai il ruolo necessario per usare questo comando!")
        return True
    return app_commands.check(predicate)


class ReportModal(discord.ui.Modal, title='Invia Report'):
    report_text = discord.ui.TextInput(
        label='Report',
        style=discord.TextStyle.long,
        placeholder='Descrivi il report...',
        required=True,
        max_length=1000
    )

    def __init__(self, membro: discord.Member):
        super().__init__()
        self.membro = membro

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = interaction.client.get_channel(REPORT_CHANNEL)
        if log_channel:
            embed = discord.Embed(title="# Report", color=0x9b59b6)
            embed.add_field(name="Player", value=self.membro.mention, inline=False)
            embed.add_field(name="Report", value=self.report_text.value, inline=False)
            embed.set_footer(text=f"Inviato da {interaction.user.display_name}")
            await log_channel.send(embed=embed)
        await interaction.response.send_message('✅ Report inviato!', ephemeral=True)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is ready: {bot.user}')
    print('Slash commands sincronizzati!')


@bot.tree.command(name='comandi', description='Mostra tutti i comandi disponibili')
async def comandi(interaction: discord.Interaction):
    testo = (
        "**📋 Comandi disponibili**\n\n"
        "**`/pex`** `@membro` `@ruolo` `[motivazione]`\n"
        "→ Aggiunge un ruolo a un membro\n\n"
        "**`/depex`** `@membro` `@vecchio_ruolo` `@nuovo_ruolo` `[motivazione]`\n"
        "→ Rimuove un ruolo e ne assegna un altro\n\n"
        "**`/promote`** `@membro` `@vecchio_ruolo` `@nuovo_ruolo` `motivazione`\n"
        "→ Promuove un membro (annuncia nel canale log)\n\n"
        "**`/demote`** `@membro` `@vecchio_ruolo` `@nuovo_ruolo` `motivazione`\n"
        "→ Retrocede un membro (annuncia nel canale log)\n\n"
        "**`/ban`** `@membro` `[motivazione]`\n"
        "→ Banna un membro dal server\n\n"
        "**`/kick`** `@membro` `[motivazione]`\n"
        "→ Kicka un membro dal server\n\n"
        "**`/timeout`** `@membro` `minuti` `[motivazione]`\n"
        "→ Mette in timeout un membro\n\n"
        "**`/warn`** `@membro` `motivazione`\n"
        "→ Avvisa un membro con un warning\n\n"
        "**`/strike`** `@membro` `1/2/3` `motivazione`\n"
        "→ Assegna uno strike a un membro\n\n"
        "**`/inattività`** `nick_in_game` `durata` `motivo`\n"
        "→ Dichiara la tua inattività (solo gang)\n\n"
        "**`/rientro`** `nick_in_game`\n"
        "→ Dichiara il tuo rientro dall'inattività (solo gang)\n\n"
        "**`/alt`** `main_account` `alt_account`\n"
        "→ Registra il tuo alt account (solo gang)\n\n"
        "**`/report`** `@membro`\n"
        "→ Invia un report su un membro\n\n"
        "*I campi tra `[ ]` sono opzionali. Gli altri sono obbligatori.*"
    )
    await interaction.response.send_message(testo, ephemeral=True)


@bot.tree.command(name='depex', description='Rimuove un ruolo e ne assegna un altro a un membro')
@app_commands.describe(
    membro='Il membro da depexare',
    vecchio_ruolo='Il ruolo da rimuovere',
    nuovo_ruolo='Il ruolo da assegnare',
    motivazione='Il motivo del depex'
)
@is_helper()
async def depex(interaction: discord.Interaction, membro: discord.Member, vecchio_ruolo: discord.Role, nuovo_ruolo: discord.Role, motivazione: str = 'Nessuna motivazione fornita'):
    try:
        await membro.remove_roles(vecchio_ruolo)
        await membro.add_roles(nuovo_ruolo)
        await interaction.response.send_message('✅ Depex eseguito!', ephemeral=True)
        log_channel = bot.get_channel(PEX_DEPEX_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(title="Depex", color=0xe74c3c)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Player", value=membro.mention, inline=False)
            embed.add_field(name="Ruolo", value=vecchio_ruolo.mention, inline=False)
            embed.add_field(name="Motivazione", value=motivazione, inline=False)
            await log_channel.send(embed=embed)
        lista_channel = bot.get_channel(LISTA_MEMBRI_CHANNEL)
        if lista_channel:
            await lista_channel.send(f"- {membro.mention}")
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi per modificare i ruoli di questo utente!', ephemeral=True)


@bot.tree.command(name='pex', description='Aggiunge un ruolo a un membro')
@app_commands.describe(
    membro='Il membro da pexare',
    ruolo='Il ruolo da assegnare',
    motivazione='Il motivo del pex'
)
@is_helper()
async def pex(interaction: discord.Interaction, membro: discord.Member, ruolo: discord.Role, motivazione: str = 'Nessuna motivazione fornita'):
    try:
        await membro.add_roles(ruolo)
        await interaction.response.send_message('✅ Pex eseguito!', ephemeral=True)
        log_channel = bot.get_channel(PEX_DEPEX_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(title="Pex", color=0x2ecc71)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nick", value=membro.mention, inline=False)
            embed.add_field(name="Da", value=f"- a {ruolo.mention}", inline=False)
            embed.add_field(name="Motivo", value=motivazione, inline=False)
            await log_channel.send(embed=embed)
        lista_channel = bot.get_channel(LISTA_MEMBRI_CHANNEL)
        if lista_channel:
            await lista_channel.send(f"+ {membro.mention} {ruolo.mention}")
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi per modificare i ruoli di questo utente!', ephemeral=True)


@bot.tree.command(name='promote', description='Promuove un membro a un nuovo ruolo')
@app_commands.describe(
    membro='Il membro da promuovere',
    vecchio_ruolo='Il ruolo da rimuovere',
    nuovo_ruolo='Il nuovo ruolo da assegnare',
    motivazione='Il motivo della promozione (obbligatorio)'
)
@is_helper()
async def promote(interaction: discord.Interaction, membro: discord.Member, vecchio_ruolo: discord.Role, nuovo_ruolo: discord.Role, motivazione: str):
    try:
        await membro.remove_roles(vecchio_ruolo)
        await membro.add_roles(nuovo_ruolo)
        await interaction.response.send_message(f'✅ {membro.mention} è stato promosso a {nuovo_ruolo.mention}!', ephemeral=True)
        log_channel = bot.get_channel(PEX_DEPEX_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(color=0x2ecc71)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nick", value=membro.mention, inline=False)
            embed.add_field(name="Da", value=f"{vecchio_ruolo.mention} a {nuovo_ruolo.mention}", inline=False)
            embed.add_field(name="Motivo", value=motivazione, inline=False)
            await log_channel.send(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi!', ephemeral=True)


@bot.tree.command(name='demote', description='Retrocede un membro a un nuovo ruolo')
@app_commands.describe(
    membro='Il membro da retrocedere',
    vecchio_ruolo='Il ruolo da rimuovere',
    nuovo_ruolo='Il nuovo ruolo da assegnare',
    motivazione='Il motivo della retrocessione (obbligatorio)'
)
@is_helper()
async def demote(interaction: discord.Interaction, membro: discord.Member, vecchio_ruolo: discord.Role, nuovo_ruolo: discord.Role, motivazione: str):
    try:
        await membro.remove_roles(vecchio_ruolo)
        await membro.add_roles(nuovo_ruolo)
        await interaction.response.send_message(f'🔻 {membro.mention} è stato retrocesso a {nuovo_ruolo.mention}!', ephemeral=True)
        log_channel = bot.get_channel(PEX_DEPEX_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(color=0xe74c3c)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nick", value=membro.mention, inline=False)
            embed.add_field(name="Da", value=f"{vecchio_ruolo.mention} a {nuovo_ruolo.mention}", inline=False)
            embed.add_field(name="Motivo", value=motivazione, inline=False)
            await log_channel.send(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi!', ephemeral=True)


@bot.tree.command(name='ban', description='Banna un membro dal server')
@app_commands.describe(
    membro='Il membro da bannare',
    motivazione='Il motivo del ban'
)
@is_helper()
async def ban(interaction: discord.Interaction, membro: discord.Member, motivazione: str = 'Nessuna motivazione fornita'):
    try:
        await membro.ban(reason=motivazione)
        await interaction.response.send_message(
            f'🔨 {membro.mention} è stato **bannato** da {interaction.user.mention}.\n'
            f'**Motivazione:** {motivazione}'
        )
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi per bannare questo utente!', ephemeral=True)


@bot.tree.command(name='kick', description='Kicka un membro dal server')
@app_commands.describe(
    membro='Il membro da kickare',
    motivazione='Il motivo del kick'
)
@is_helper()
async def kick(interaction: discord.Interaction, membro: discord.Member, motivazione: str = 'Nessuna motivazione fornita'):
    try:
        await membro.kick(reason=motivazione)
        await interaction.response.send_message(
            f'👢 {membro.mention} è stato **kickato** da {interaction.user.mention}.\n'
            f'**Motivazione:** {motivazione}'
        )
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi per kickare questo utente!', ephemeral=True)


@bot.tree.command(name='timeout', description='Mette in timeout un membro')
@app_commands.describe(
    membro='Il membro da mettere in timeout',
    minuti='Durata del timeout in minuti',
    motivazione='Il motivo del timeout'
)
@is_helper()
async def timeout(interaction: discord.Interaction, membro: discord.Member, minuti: int, motivazione: str = 'Nessuna motivazione fornita'):
    if minuti <= 0:
        await interaction.response.send_message('La durata del timeout deve essere almeno 1 minuto!', ephemeral=True)
        return
    try:
        duration = datetime.timedelta(minutes=minuti)
        await membro.timeout(duration, reason=motivazione)
        await interaction.response.send_message(
            f'⏱️ {membro.mention} è stato messo in **timeout** per **{minuti} minuti** da {interaction.user.mention}.\n'
            f'**Motivazione:** {motivazione}'
        )
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi per mettere in timeout questo utente!', ephemeral=True)


@bot.tree.command(name='warn', description='Avvisa un membro con un warning')
@app_commands.describe(
    membro='Il membro da avvisare',
    motivazione='Il motivo del warning'
)
@is_helper()
async def warn(interaction: discord.Interaction, membro: discord.Member, motivazione: str):
    try:
        try:
            await membro.send(
                f"⚠️ Hai ricevuto un **warning** nel server.\n"
                f"**Motivo:** {motivazione}\n"
                f"*Eseguito da: {interaction.user.display_name}*"
            )
            dm_inviato = True
        except discord.Forbidden:
            dm_inviato = False

        await interaction.response.send_message(
            f'⚠️ {membro.mention} ha ricevuto un warning da {interaction.user.mention}.\n'
            f'**Motivazione:** {motivazione}'
            + ('' if dm_inviato else '\n*(DM non inviato: l\'utente ha i DM chiusi)*'),
            ephemeral=True
        )
        log_channel = bot.get_channel(PEX_DEPEX_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(color=0xf39c12)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nick", value=membro.mention, inline=False)
            embed.add_field(name="Motivo", value=motivazione, inline=False)
            if not dm_inviato:
                embed.set_footer(text="⚠️ DM non inviato: l'utente ha i DM chiusi")
            await log_channel.send(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi!', ephemeral=True)


@bot.tree.command(name='strike', description='Assegna uno strike a un membro')
@app_commands.describe(
    membro='Il membro a cui assegnare lo strike',
    numero='Numero dello strike (1, 2 o 3)',
    motivazione='Il motivo dello strike'
)
@app_commands.choices(numero=[
    app_commands.Choice(name='Strike 1', value=1),
    app_commands.Choice(name='Strike 2', value=2),
    app_commands.Choice(name='Strike 3', value=3),
])
@is_helper()
async def strike(interaction: discord.Interaction, membro: discord.Member, numero: int, motivazione: str):
    try:
        if numero == 1:
            ruolo_strike = interaction.guild.get_role(RUOLO_STRIKE1)
            if ruolo_strike:
                await membro.add_roles(ruolo_strike)
        elif numero == 2:
            ruolo_strike = interaction.guild.get_role(RUOLO_STRIKE2)
            if ruolo_strike:
                await membro.add_roles(ruolo_strike)

        try:
            await membro.send(
                f"Esecutore: {interaction.user.mention}\n"
                f"Numero strike: {numero}\n"
                f"Motivazione: {motivazione}"
            )
            dm_inviato = True
        except discord.Forbidden:
            dm_inviato = False

        await interaction.response.send_message(
            f'{membro.mention} ha ricevuto lo **Strike {numero}** da {interaction.user.mention}.\n'
            f'**Motivazione:** {motivazione}'
            + ('' if dm_inviato else '\n*(DM non inviato: l\'utente ha i DM chiusi)*'),
            ephemeral=True
        )
        log_channel = bot.get_channel(STRIKE_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(title="Strike", color=0xf1c40f)
            embed.add_field(name="Esecutore", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nick", value=membro.mention, inline=False)
            embed.add_field(name="Strike", value=f"**{numero}**", inline=False)
            embed.add_field(name="Motivazione", value=motivazione, inline=False)
            if not dm_inviato:
                embed.set_footer(text="⚠️ DM non inviato: l'utente ha i DM chiusi")
            await log_channel.send(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message('Non ho i permessi!', ephemeral=True)


@bot.tree.command(name='inattività', description='Dichiara la tua inattività')
@app_commands.describe(
    nick_in_game='Il tuo nick in game',
    durata='Durata dell\'inattività (es: 3 giorni, 1 settimana)',
    motivo='Il motivo dell\'inattività'
)
@is_gang()
async def inattivita(interaction: discord.Interaction, nick_in_game: str, durata: str, motivo: str):
    ruolo_inattivo = interaction.guild.get_role(RUOLO_INATTIVO)
    if ruolo_inattivo:
        await interaction.user.add_roles(ruolo_inattivo)
    embed = discord.Embed(color=0x95a5a6)
    embed.add_field(name="Nick in game", value=nick_in_game, inline=False)
    embed.add_field(name="Durata", value=durata, inline=False)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.set_footer(text=f"Dichiarato da {interaction.user.display_name}")
    log_channel = bot.get_channel(INATTIVITA_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)
    await interaction.response.send_message('✅ Inattività dichiarata!', ephemeral=True)


@bot.tree.command(name='rientro', description='Dichiara il tuo rientro dall\'inattività')
@app_commands.describe(
    nick_in_game='Il tuo nick in game'
)
@is_gang()
async def rientro(interaction: discord.Interaction, nick_in_game: str):
    ruolo_inattivo = interaction.guild.get_role(RUOLO_INATTIVO)
    ruolo_rientro = interaction.guild.get_role(RUOLO_RIENTRO)
    if ruolo_inattivo:
        await interaction.user.remove_roles(ruolo_inattivo)
    if ruolo_rientro:
        await interaction.user.add_roles(ruolo_rientro)
    embed = discord.Embed(color=0x2ecc71)
    embed.add_field(name="Nick in game", value=nick_in_game, inline=False)
    embed.add_field(name="Stato", value="✅ Rientrato dall'inattività", inline=False)
    embed.set_footer(text=f"Dichiarato da {interaction.user.display_name}")
    log_channel = bot.get_channel(INATTIVITA_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)
    await interaction.response.send_message('✅ Rientro dichiarato!', ephemeral=True)


@bot.tree.command(name='alt', description='Registra il tuo alt account')
@app_commands.describe(
    main_account='Il tuo main account',
    alt_account='Il tuo alt account'
)
@is_gang()
async def alt(interaction: discord.Interaction, main_account: str, alt_account: str):
    embed = discord.Embed(title="# Alt", color=0x3498db)
    embed.add_field(name="Main account", value=main_account, inline=False)
    embed.add_field(name="Alt Account", value=alt_account, inline=False)
    embed.set_footer(text=f"Registrato da {interaction.user.display_name}")
    log_channel = bot.get_channel(ALT_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)
    await interaction.response.send_message('✅ Alt account registrato!', ephemeral=True)


@bot.tree.command(name='report', description='Invia un report su un membro')
@app_commands.describe(
    membro='Il membro da reportare'
)
@is_report_role()
async def report(interaction: discord.Interaction, membro: discord.Member):
    await interaction.response.send_modal(ReportModal(membro))


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message('Non hai il ruolo necessario per usare questo comando!', ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('Non hai i permessi per usare questo comando!', ephemeral=True)
    else:
        await interaction.response.send_message('Si è verificato un errore.', ephemeral=True)
        raise error


bot.run('TOKEN')
