import random
# from asyncio import sleep
from datetime import time, timedelta, timezone, datetime

from discord import ButtonStyle, Client, Embed, File
from discord.ext import tasks
from discord.ui import Button, View

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
        await channel.send(next_event.url, silent=True)  # 次のイベントのURL送信

        # バトスタの場合
        if next_event.name == "BATTLE STADIUM":

            # gif
            await channel.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
            return
            # バトスタ通知を送ったらここで終了

    # generalの最新メッセージがbotのメッセージなら終了
    async for message in channel.history(limit=1):
        if message.author.bot:
            return

    # 毎週土曜のみ通話開始通知ロールの宣伝
    dt_now = datetime.now(JST)
    if dt_now.weekday() in [2, 5]:

        embed = Embed(
            title="通話開始 お知らせ機能",
            description="誰かがボイスチャンネルに入ったときに通知ほしい人は下のボタンを押してください。\n通知ボタンを押すと誰かがボイスチャンネルに入ったときに通知が来るよ！\nビートボックス出来ないよー聞き専だよーって人でも大丈夫！ボタン押して！さ、早く！\nもし通知うるさいなーって思ったら、下のボタンをもう1回押すとロールが外れるよ！",
            color=0x00bfff
        )
        button = Button(
            label="通話開始 お知らせロール",
            style=ButtonStyle.primary,
            custom_id="button_notify_voice",
            emoji="🔔"
        )
        view = View(timeout=None)
        view.add_item(button)

        await channel.send(embed=embed, view=view, silent=True)

    # 他はフォーラムの宣伝
    else:
        forum_solo = client.get_channel(database.FORUM_SOLO)
        forum_loop = client.get_channel(database.FORUM_LOOP)

        embed = Embed(
            title="質問きてた！ 👇",
            description=f"{forum_loop.jump_url}\n{forum_solo.jump_url}\n\nどんどん質問してね！",
            color=0x00bfff
        )
        embed.set_footer(
            text="ビト森無料相談～♪",
            icon_url=channel.guild.icon.url
        )
        await channel.send(embed=embed, silent=True)

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
