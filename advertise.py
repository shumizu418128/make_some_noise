import random
from asyncio import sleep
from datetime import datetime, time, timedelta, timezone

from discord import Client, Embed, File
from discord.ext import tasks

from battle_stadium import start
from search_next_event import search_next_event

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)


@tasks.loop(time=PM9)
async def advertise(client: Client):
    channel = client.get_channel(864475338340171791)  # 全体チャット
    # 次のイベント
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event) and next_event.name == "BATTLE STADIUM":  # バトスタの場合
        # gif
        await channel.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
    await channel.send(next_event.url)  # 次のイベントのURL送信
    dt_now = datetime.now(JST)  # 現在時刻

    # バトスタ開始まで35分以内の場合
    if next_event.name == "BATTLE STADIUM" and next_event.start_time - dt_now < timedelta(minutes=35):
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

    # TODO エントリー開始時、有効化
    """view = await get_view_contact(cancel=False, confirm=False)
    await channel.send("第3回ビト森杯", view=view)"""
