import random
# from asyncio import sleep
from datetime import time, timedelta, timezone  # , datetime

from discord import Client, File  # , Embed
from discord.ext import tasks
import database
# from button_view import get_view
# from battle_stadium import start
from search_next_event import search_next_event

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)


@tasks.loop(time=PM9)
async def advertise(client: Client):
    channel = client.get_channel(database.CHANNEL_GENERAL)

    # 次のイベント
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event):
        await channel.send(next_event.url)  # 次のイベントのURL送信

        # バトスタの場合
        if next_event.name == "BATTLE STADIUM":

            # gif
            await channel.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))

    # ランダムに通話通知オンroleつけちゃうw
    role = channel.guild.get_role(database.ROLE_CALL_NOTIFY)

    # メンバーを10人選んでroleつける
    members = role.guild.members
    random.shuffle(members)

    for member in members[:10]:

        # 運営とbotは除外
        if member.get_role(database.ROLE_ADMIN) is None and member.bot is False:
            try:
                await member.add_roles(role)
            except Exception as e:
                print(e)
                pass

    ##############################
    # 以下無期限凍結
    ##############################
    """
    # バトスタ開始まで35分以内の場合
    if next_event.name == "BATTLE STADIUM" and next_event.start_time - dt_now < timedelta(minutes=35):
        dt_now = datetime.now(JST)  # 現在時刻
        minute = 60
        await sleep(29 * minute)  # 29分待機
        embed = Embed(title="BATTLE STADIUM 開始ボタン",
                      description="▶️を押すとバトスタを開始します")
        bot_channel = client.get_channel(930447365536612353)  # バトスタbot
        battle_stadium_start = await bot_channel.send(embed=embed)
        await battle_stadium_start.add_reaction("▶️")
        await battle_stadium_start.add_reaction("❌")

        def check(reaction, user):
            stamps = ["▶️", "❌"]
            role_check = user.get_role(1096821566114902047)  # バトスタ運営
            return bool(role_check) and reaction.emoji in stamps and reaction.message == battle_stadium_start
        try:
            # 10分待機
            reaction, _ = await client.wait_for('reaction_add', check=check, timeout=600)
            await battle_stadium_start.clear_reactions()
        except TimeoutError:  # 10分経過ならさよなら
            await battle_stadium_start.clear_reactions()
            return
        if reaction.emoji == "❌":  # ❌ならさよなら
            await battle_stadium_start.delete()
        await start(client)
    """
    return
