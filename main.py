import discord
from datetime import datetime
import pytz
from discord import ButtonStyle, ui, app_commands
from dotenv import load_dotenv
from os import getenv

load_dotenv()
TOKEN = getenv("TOKEN")
GUILD = getenv('DISCORD_GUILD_ID')
CHANNEL = getenv('IDEA_CHANNEL_ID')
ROLE = getenv('ROLE_TO_MENTION_ID').replace(" ", "").split(',')
ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN = eval(getenv('ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN'))

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        client.add_view(View())
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=GUILD))
            self.synced = True
        print(f"Bot has logged in as {self.user}.")


class IdeaModal(ui.Modal, title="Misery Idea"):
    idea_title = ui.TextInput(
        label='Idea Title',
        style=discord.TextStyle.short,
        placeholder="Please provide a brief title for your idea",
        required=True,
        min_length=5,
        max_length=100
    )
    idea_desc = ui.TextInput(
        label='Idea Description',
        style=discord.TextStyle.paragraph,
        placeholder="Please provide a description for your idea",
        required=True,
        min_length=5,
        max_length=4000
    )  

    if ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN:
        idea_anon_select = ui.Select(
            placeholder="", 
        )
        idea_anon_select.add_option(
            label="Do Not Submit Anonymously",
            value='False'
        )
        idea_anon_select.add_option(
            label="Submit Anonymously",
            value='True'
        )
    
    async def on_submit(self, interaction: discord.Interaction):
        idea_author = interaction.user.display_name
        embed = discord.Embed(title=self.idea_title, description=f"{self.idea_desc}")

        if ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN:
            submit_as_anonymous = self.idea_anon_select.values[0]
        
        if ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN and submit_as_anonymous == 'True':
            embed.set_author(name="Anonymous Submission")
        else:
            embed.set_author(name=idea_author)

        channel = client.get_channel(int(CHANNEL))
        await channel.send(content=f"{format_mention()}\n", embed=embed, view=View())
        await interaction.response.send_message(
            f'Your idea has been sent to Misery staff{" anonymously" if ENABLE_ANONYMOUS_SUBMISSION_DROPDOWN and submit_as_anonymous == "True" else ""}. Thank you, {idea_author}!', embed=embed,
            ephemeral=True)


class View(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.role_mention = None

    approve_Button = None
    decline_Button = None
    decision = None

    @ui.button(label="Approve", custom_id="approve", style=ButtonStyle.green)
    async def approve_callback(self, interaction, button):
        self.approve_Button = button

        embed = edit_message_embed(embed=interaction.message.embeds[0],
                                   display_name=interaction.user.display_name,
                                   color=discord.Color.green(),
                                   decision="approved")
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Decline", custom_id="decline", style=ButtonStyle.red)
    async def decline_callback(self, interaction, button):
        self.decline_Button = button

        embed = edit_message_embed(embed=interaction.message.embeds[0],
                                   display_name=interaction.user.display_name,
                                   color=discord.Color.red(),
                                   decision="declined")
        await interaction.response.edit_message(embed=embed, view=self)


def edit_message_embed(embed, display_name, color, decision):
    edited_embed = embed
    edited_embed.color = color
    edited_embed.set_footer(text=f"-------------------------------------------------\n"
                                 f"{display_name} has {decision} this idea!\n"
                                 f"{datetime.now(tz=pytz.timezone('US/Pacific')).strftime('%I:%M:%S %p %Z')}\n"
                                 f"{datetime.now().strftime('%A, %B %d, %Y')}")
    return edited_embed


client = Client()
tree = app_commands.CommandTree(client)


@tree.command(name="idea",
              description="Submit an idea you have for Misery Company. "
                          "A temporary receipt will be displayed upon submission.",
              guild=discord.Object(id=GUILD))
async def modal(interaction: discord.Interaction):
    await interaction.response.send_modal(IdeaModal())


def format_mention():
    formatted_role = ""
    for role in ROLE:
        formatted_role = formatted_role + "<@&" + role + ">"
    return formatted_role


client.run(TOKEN)
