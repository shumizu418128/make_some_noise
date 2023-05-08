import asyncio
import datetime
import random
from asyncio import sleep

from discord import (ButtonStyle, Client, Embed, FFmpegPCMAudio, File, Message,
                     PCMVolumeTransformer, VoiceClient, Interaction)
from discord.ui import Button, View


async def battle(text: str, client: Client):
    stamps = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣"}
    stage_channel = client.get_channel(931462636019802123)  # ステージ
    chat = stage_channel
    pairing_channel = client.get_channel(930767329137143839)  # 対戦表
    entry_channel = client.get_channel(930446820839157820)  # 参加
    bot_channel = client.get_channel(930447365536612353)  # bot
    vc_role = chat.guild.get_role(935073171462307881)  # in a vc
    JST = datetime.timezone(datetime.timedelta(hours=9))
    embed_chat_info = Embed(title="チャット欄はこちら `chat is here`",
                            description=f"対戦表 `pairing`： {pairing_channel.mention}\nエントリー `entry`： {entry_channel.mention}\nBATTLEタイマー `timer`： {bot_channel.mention}", color=0x00bfff)
    count = 0
    names = text.replace(" vs", "").replace('s.battle', '').split()
    auto = False
    if len(names) == 3:
        try:
            count = int(names[2])
        except ValueError:
            pass
        if 1 <= count <= 4:
            embed = Embed(
                title="バトル再開モード", description=f"Round {stamps[count]}: **{names[1 - count % 2]}**\nから、バトルを再開します。", color=0x00bfff)
            await bot_channel.send(embed=embed)
            await chat.send(embed=embed)
        if names[2] == "auto":
            del names[2]
            auto = True
    embed = Embed(title="処理中...")
    before_start = await bot_channel.send(embed=embed)
    if len(names) == 2:  # 順番を抽選で決定（通常スタート）
        count = 1
        embed = Embed(title="先攻・後攻の抽選を行います", description="抽選中...")
        await before_start.edit(embed=embed)
        random.shuffle(names)
        await sleep(1)

    if count == 0 or count > 4:  # countが0 == nameの取得失敗
        embed = Embed(title="Error: 対戦カード読み込み失敗",
                      description=f"入力内容：{names}\n\n`cancelと入力するとキャンセルできます`\n↓もう一度入力してください↓", color=0xff0000)
        await bot_channel.send(embed=embed)

        def check(message):
            role_check = message.author.get_role(1096821566114902047)  # バトスタ運営
            return message.channel == bot_channel and bool(role_check)
        try:
            message = await client.wait_for('message', timeout=600, check=check)
        except asyncio.TimeoutError:
            await bot_channel.send("Error: timeout")
            return False
        if message.content == "cancel":
            await bot_channel.send("キャンセルしました。")
            return False
        await battle(message.content, client)
        return

    async def connection(voice_client: VoiceClient):
        if voice_client.is_connected() is False:
            try:
                await stage_channel.connect(reconnect=True)
                await chat.guild.me.edit(suppress=False)
            except Exception:
                embed = Embed(
                    title="Error", description="接続が失われたため、タイマーを停止しました\nlost connection\n\nまもなく、自動でバトル再開準備を行います", color=0xff0000)
                await bot_channel.send(embed=embed)
                await chat.send(embed=embed)
                await sleep(3)
                await bot_channel.send(f"----------\n\n再開コマンド自動入力：{names[0]} vs {names[1]} Round{count}\n\n----------")
                await battle(f"{names[0]} {names[1]} {count}", client)
                return False
            else:
                print("lost connection: auto reconnect done")

    async def timer(time: float, message: Message, voice_client: VoiceClient, count: int):
        connect = await connection(voice_client)
        if connect is False:
            return False

        def check(reaction, user):
            role_check = user.get_role(1096821566114902047)  # バトスタ運営
            return bool(role_check) and str(reaction.emoji) == '❌' and reaction.message == message
        try:
            _, _ = await client.wait_for('reaction_add', timeout=time, check=check)
        except asyncio.TimeoutError:
            connect = await connection(voice_client)
            if connect is False:
                return False
        else:
            audio = PCMVolumeTransformer(FFmpegPCMAudio("timer_stop.mp3"))
            try:
                voice_client.stop()
                chat.guild.voice_client.play(audio)
            except Exception:
                pass
            embed = Embed(title="TIMER STOPPED",
                          description="問題が発生したため、タイマーを停止しました\ntimer stopped due to a problem\n\nまもなく、自動でバトル再開準備を行います", color=0xff0000)
            await bot_channel.send(embed=embed)
            await chat.send(embed=embed)
            await sleep(3)
            await bot_channel.send(f"----------\n\n再開コマンド自動入力：{names[0]} vs {names[1]} Round{count}\n\n----------")
            await battle(f"{names[0]} {names[1]} {count}", client)
            return False

    embed = Embed(title=f"1️⃣ {names[0]} vs {names[1]} 2️⃣",
                  description=f"1分・2ラウンドずつ\n`1 minute, 2 rounds each`\n\n>先攻：__**{names[0]}**__")
    embed.timestamp = datetime.datetime.now(JST)
    if len(names) == 2:  # 通常スタート時
        embed.description += "\n`（抽選で決定されました）`"
    if auto:
        embed.description += "\n\nℹ️ コマンド自動入力機能により自動設定されました"
    await before_start.edit(embed=embed)
    await chat.send(embed=embed)
    await before_start.add_reaction("▶️")
    await before_start.add_reaction("❌")

    def check(reaction, user):
        stamps = ["▶️", "❌"]
        role_check = user.get_role(1096821566114902047)  # バトスタ運営
        return bool(role_check) and reaction.emoji in stamps and reaction.message == before_start
    reaction, _ = await client.wait_for('reaction_add', check=check)
    await before_start.clear_reactions()
    if reaction.emoji == "❌":
        await before_start.delete()
        return False
    voice_client = chat.guild.voice_client
    if voice_client is None:
        voice_client = await stage_channel.connect(reconnect=True)
    await chat.guild.me.edit(suppress=False)
    embed = Embed(title="Are you ready??", color=0x00ff00)
    sent_message = await bot_channel.send(embed=embed)
    await sent_message.add_reaction("❌")
    embed.description = f"BATTLEタイマーはこちら {bot_channel.mention}"
    await chat.send(embed=embed)
    random_start = random.randint(1, 3)
    audio = PCMVolumeTransformer(FFmpegPCMAudio(
        f"BattleStart_{random_start}.mp3"), volume=0.4)
    chat.guild.voice_client.play(audio)
    if random_start == 1:
        check_timer = await timer(9, sent_message, voice_client, count)
        if check_timer is False:
            return False
    else:
        check_timer = await timer(11, sent_message, voice_client, count)
        if check_timer is False:
            return False
    embed = Embed(title="🔥🔥 3, 2, 1, Beatbox! 🔥🔥", color=0xff0000)
    await sent_message.edit(embed=embed)
    embed.description = f"BATTLEタイマーはこちら {bot_channel.mention}"
    await chat.send(embed=embed)
    check_timer = await timer(3, sent_message, voice_client, count)
    if check_timer is False:
        return False

    while count <= 4:
        embed = Embed(
            title="1:00", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=0x00ff00)
        await sent_message.edit(embed=embed)
        await chat.send(embed=embed, delete_after=10)
        counter = 50
        color = 0x00ff00
        for i in range(5):
            check_timer = await timer(9.9, sent_message, voice_client, count)
            if check_timer is False:
                return False
            embed = Embed(
                title=f"{counter}", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=color)
            await sent_message.edit(embed=embed)
            await chat.send(embed=embed, delete_after=5)
            counter -= 10
            if i == 0:
                embed = Embed(title="音声バグが発生する場合があります",
                              description=f"Beatboxerの音声が聞こえない場合、チャットにてお知らせください\n`タイマーを停止し、バトルを中断することがあります`\n\nBATTLEタイマーはこちら {bot_channel.mention}", color=0xffff00)
                await chat.send(embed=embed, delete_after=50)
            if i == 1:
                color = 0xffff00
            if i == 3:
                color = 0xff0000
        check_timer = await timer(4.9, sent_message, voice_client, count)
        if check_timer is False:
            return False
        embed = Embed(
            title="5", description=f"Round {stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} vs {names[1]}", color=color)
        await sent_message.edit(embed=embed)
        await chat.send(embed=embed, delete_after=5)
        check_timer = await timer(4.9, sent_message, voice_client, count)
        if check_timer is False:
            return False
        if count <= 3:
            audio = PCMVolumeTransformer(FFmpegPCMAudio(
                f"round{count + 1}switch_{random.randint(1, 3)}.mp3"), volume=2)
            chat.guild.voice_client.play(audio)
            embed = Embed(
                title="TIME!", description=f"Round {stamps[count + 1]}  **{names[count % 2]}**\nSWITCH!\n\n{names[0]} vs {names[1]}")
            await sent_message.edit(embed=embed)
            await chat.send(embed=embed, delete_after=3)
            check_timer = await timer(3, sent_message, voice_client, count)
            if check_timer is False:
                return False
        count += 1
    audio = PCMVolumeTransformer(FFmpegPCMAudio(f"time_{random.randint(1, 2)}.mp3"), volume=0.5)
    await sent_message.delete()
    tari3210 = chat.guild.get_member(412082841829113877)
    embed = Embed(title="投票箱（集計は行いません）", description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\n>>> BATTLE STADIUM\n毎週土曜21:30~ 開催中！", color=0x00bfff)
    embed.set_footer(text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
    embed.timestamp = datetime.datetime.now(JST)
    if random.randint(1, 20) == 1:
        audio = PCMVolumeTransformer(FFmpegPCMAudio("time_fuga.mp3"), volume=0.4)
        chat.guild.voice_client.play(audio)
        await sleep(7)
        poll = await bot_channel.send(f"{vc_role.mention}\nなあああああああああああああああああああああああああああああああああああああああああああああああああああああああああ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！", embed=embed)
        await poll.add_reaction("1⃣")
        await poll.add_reaction("2⃣")
        await poll.add_reaction("🦁")
        await chat.send(embed=embed_chat_info)
        return
    chat.guild.voice_client.play(audio)
    poll = await bot_channel.send(f"{vc_role.mention}\nmake some noise for the battle!\ncome on!!", embed=embed)
    await poll.add_reaction("1⃣")
    await poll.add_reaction("2⃣")
    await poll.add_reaction("🔥")
    audio = PCMVolumeTransformer(FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.7)
    await sleep(3.9)
    chat.guild.voice_client.play(audio)
    await chat.send("make some noise for the battle!\ncome on!!", embed=embed_chat_info)
    return


"""
s.start コマンド
"""


async def start(client: Client):
    bot_channel = client.get_channel(930447365536612353)  # bot
    stage_channel = client.get_channel(931462636019802123)  # ステージ
    chat = stage_channel
    bbx_mic = client.get_channel(931781522808262756)  # bbxマイク設定
    pairing_channel = client.get_channel(930767329137143839)  # 対戦表
    entry_channel = client.get_channel(930446820839157820)  # 参加
    general = client.get_channel(864475338340171791)  # 全体チャット
    bs_role = chat.guild.get_role(930368130906218526)  # BATTLE STADIUM
    vc_role = chat.guild.get_role(935073171462307881)  # in a vc
    scheduled_events = chat.guild.scheduled_events
    embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                            description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nBATTLEタイマー： {bot_channel.mention}", color=0x00bfff)
    await chat.send("ただいま準備中...", embed=embed_chat_info)
    await bot_channel.send("処理中...")
    try:
        for scheduled_event in scheduled_events:
            if scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.start()
                break
        await stage_channel.create_instance(topic="BATTLE STADIUM", send_notification=True)
    except Exception:
        pass
    await general.send(stage_channel.jump_url, file=File("battle_stadium.gif"))
    if chat.guild.voice_client is None:
        await stage_channel.connect(reconnect=True)
    await chat.guild.me.edit(suppress=False)
    await pairing_channel.purge()
    for member in bs_role.members:
        await member.remove_roles(bs_role)
    button = Button(label="Entry", style=ButtonStyle.primary, emoji="✅")

    async def button_callback(interaction: Interaction):
        await interaction.response.defer(ephemeral=True, thinking=False)
        await interaction.user.add_roles(bs_role)
        embed = Embed(title="受付完了 entry completed",
                      description=f"**【注意事項】**\n- ノイズキャンセル設定に問題がある方が非常に増えています。必ず {bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。\n- Discordの音声バグが多発しています。発生した場合、バトルを中断し、途中のラウンドからバトルを再開することがあります。\n※音声バグ発生時の対応は状況によって異なります。ご了承ください。", color=0xffff00)
        await bot_channel.send(f"エントリー完了：{interaction.user.display_name}", delete_after=3)
        await interaction.followup.send(embed=embed, ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    embed = Embed(
        title="Entry", description="下のボタンを押してエントリー！\npress button to entry")
    entry_button = await entry_channel.send(vc_role.mention, embed=embed, view=view)
    audio = PCMVolumeTransformer(FFmpegPCMAudio("announce.mp3"))
    chat.guild.voice_client.play(audio)
    embed = Embed(
        title="受付開始", description=f"ただいまより参加受付を開始します。\n{entry_channel.mention}にてエントリーを行ってください。\nentry now accepting at {entry_channel.mention}", color=0x00bfff)
    await bot_channel.send(embed=embed)
    await entry_channel.send(f"エントリー後に {bbx_mic.mention} を確認して、マイク設定を行ってください。", delete_after=60)
    await sleep(5)
    entry_button2 = await chat.send("このボタンからもエントリーできます", embed=embed, view=view)
    await sleep(20)
    embed = Embed(title="あと30秒で締め切ります", color=0xffff00)
    await bot_channel.send(embed=embed)
    await chat.send(embed=embed_chat_info)
    await entry_channel.send(f"{vc_role.mention}\nボタンを押してエントリー！\npress button to entry", delete_after=30)
    await sleep(20)
    embed = Embed(title="バトル中に、音声バグが発生する場合があります",
                  description=f"Beatboxerの音声が聞こえない場合、チャットにてお知らせください\n`タイマーを停止し、バトルを中断することがあります`\n\nBATTLEタイマーはこちら {bot_channel.mention}", color=0xffff00)
    await chat.send(embed=embed)
    embed = Embed(title="締め切り10秒前", color=0xff0000)
    await bot_channel.send(embed=embed)
    await sleep(10)
    await entry_button.delete()
    await entry_button2.delete()
    await bot_channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
    playerlist = [member.display_name.replace("`", "").replace(
        " ", "-") for member in bs_role.members]
    if len(playerlist) < 2:
        embed = Embed(title="Error", description="参加者が不足しています。",
                      color=0xff0000)
        await bot_channel.send(embed=embed)
        return
    random.shuffle(playerlist)
    counter = 1
    counter2 = 0
    embed_pairing = Embed(
        title="抽選結果", description="先攻・後攻は、バトル直前に抽選を行い決定します", color=0xff9900)
    while counter2 + 2 <= len(playerlist):
        embed_pairing.add_field(
            name=f"Match{counter}", value=f"{playerlist[counter2]} vs {playerlist[counter2 + 1]}", inline=False)
        counter += 1
        counter2 += 2
    if len(playerlist) % 2 == 1:
        double_pl = chat.guild.get_member_named(playerlist[0])
        if double_pl is None:
            double_pl = playerlist[0]
        else:
            double_pl = double_pl.mention
        embed = Embed(title="参加人数が奇数でした",
                      description=f"{playerlist[0]}さんの対戦が2回行われます\n\n※あと1人参加者が追加された場合、{playerlist[0]}さんと交代になります。", color=0xff9900)
        await bot_channel.send(embed=embed)
        await pairing_channel.send(f"参加人数が奇数でした。\n{double_pl}さんの対戦が2回行われます。\n\n※あと1人参加者が追加された場合、{double_pl}さんと交代になります。")
        embed = Embed(title="参加人数が奇数でした",
                      description=f"あと1人参加できます。ご希望の方はこのチャットにご記入ください。\n\n※参加者が追加された場合、{playerlist[0]}さんと交代になります。", color=0xff9900)
        await chat.send(embed=embed)
        embed_pairing.add_field(
            name=f"Match{counter}", value=f"{playerlist[-1]} vs {playerlist[0]}", inline=False)
    tari3210 = chat.guild.get_member(412082841829113877)
    embed_pairing.set_footer(
        text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
    JST = datetime.timezone(datetime.timedelta(hours=9))
    embed_pairing.timestamp = datetime.datetime.now(JST)
    await bot_channel.send(embed=embed_pairing)
    embed_pairing.title = "対戦カード"
    await pairing_channel.send(vc_role.mention, embed=embed_pairing)
    await pairing_channel.send(f"{bs_role.mention}\n\n{bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。")
    await chat.send(embeds=[embed_pairing, embed_chat_info])
    for i in range(0, len(playerlist), 2):
        await bot_channel.send(f"----------\n\ns.battleコマンド自動入力\n{playerlist[0]} vs {playerlist[1]}\nMatch{i / 2 + 1}\n\n----------")
        try:
            battle_continue = await battle(f"{playerlist[i]} {playerlist[i + 1]} auto", client)
        except IndexError:  # 参加者数が奇数のとき発生
            embed = Embed(title="最終マッチを行います", description="対戦カードが変更されている場合、❌を押してs.battleコマンドを入力しなおしてください", color=0x00bfff)
            await bot_channel.send(embed=embed)
            await bot_channel.send(f"----------\n\ns.battleコマンド自動入力\n{playerlist[0]} vs {playerlist[1]}\nMatch{i / 2 + 1}\n\n----------")
            battle_continue = await battle(f"{playerlist[-1]} {playerlist[0]} auto", client)
        if battle_continue is False:
            embed = Embed(title="自動入力中止", description="s.battleコマンド自動入力を中止します\ns.battle [名前1] [名前2] と入力してください", color=0xff0000)
            await bot_channel.send(embed=embed)
            return

    embed = Embed(title="ラストMatchが終了しました", description="ご参加ありがとうございました！\nmake some noise for all of amazing performance!!", color=0x00bfff)
    await bot_channel.send(embed=embed)
    await chat.send(embed=embed)
