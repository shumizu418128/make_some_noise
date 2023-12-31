from datetime import datetime, timedelta, timezone
from discord import Embed, Member

from contact import search_contact

JST = timezone(timedelta(hours=9))


async def debug_log(function_name: str, description: str, color: int, member: Member):
    bot_channel = member.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = member.guild.get_member(
        412082841829113877  # tari3210
    )
    thread = await search_contact(member)
    embed = Embed(
        title=function_name,
        description=f"{description}\n\n{member.mention}\n{thread.jump_url}\
            \n[スプレッドシート](https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0)",
        color=color
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )
    embed.timestamp = datetime.now(JST)

    if color == 0xff0000:
        await bot_channel.send(f"{tari3210.mention}\n{member.id}", embed=embed)
    else:
        await bot_channel.send(f"{member.id}", embed=embed)
