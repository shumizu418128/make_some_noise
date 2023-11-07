import asyncio
import random
from asyncio import sleep
from datetime import datetime, timedelta, timezone

from discord import (ButtonStyle, Client, Embed, EventStatus, FFmpegPCMAudio,
                     File, Interaction, Message, PCMVolumeTransformer,
                     PrivacyLevel, VoiceClient)
from discord.ui import Button, View

"""
battle status について
None: battle続行可能
battle_skip: battleを終了し、次のbattleをスタートする
battle_reschedule: battleを一旦スキップし、最終マッチ後に追加）
battle_error: battleを強制終了、自動入力中止
"""
JST = timezone(timedelta(hours=9))


async def battle(text: str, client: Client):
    # 初期設定
    stamps = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣"}
    stage_channel = client.get_channel(931462636019802123)  # ステージ
    chat = stage_channel
    pairing_channel = client.get_channel(930767329137143839)  # 対戦表
    entry_channel = client.get_channel(930446820839157820)  # 参加
    bot_channel = client.get_channel(930447365536612353)  # bot
    maiku_check = client.get_channel(1115986804026392627)  # maiku_check
    vc_role = chat.guild.get_role(935073171462307881)  # in a vc
    tari3210 = chat.guild.get_member(412082841829113877)
    embed_chat_info = Embed(title="チャット欄はこちら `chat is here`",
                            description=f"対戦表 `pairing`： {pairing_channel.mention}\nエントリー `entry`： {entry_channel.mention}\nBATTLEタイマー `timer`： {bot_channel.mention}\nマイクチェック： {maiku_check.mention}", color=0x00bfff)
    embed_maiku_check = Embed(
        title="事前マイクチェックをご利用ください", description=f"事前にマイク設定画面のスクショを提出して、botによるマイクチェックを受けてください\n\nマイクチェックチャンネルはこちら {maiku_check.mention}", color=0xffff00)
    count = 0

    # マ イ ク チ ェ ッ ク を し ろ
    await chat.send(embed=embed_maiku_check)

    # 名前整理
    names = text.replace(" vs", "").replace('s.battle', '').split()  # 名前を分割
    if len(names) == 3:  # ラウンド指定あり
        try:
            count = int(names[2])
        except ValueError:  # ラウンド指定が数字になっていない
            pass
        if 1 <= count <= 4:  # ラウンド指定が適切
            embed = Embed(
                title="バトル再開モード", description=f"Round {stamps[count]}: **{names[1 - count % 2]}**\nから、バトルを再開します。", color=0x00bfff)
            await bot_channel.send(embed=embed)
            await chat.send(embed=embed)

        last_match = False
        if names[2] == "last":  # 最終マッチ
            del names[2]
            last_match = True

    embed = Embed(title="処理中...")
    before_start = await bot_channel.send(embed=embed)  # 処理中パネル
    if len(names) == 2:  # 順番を抽選で決定（通常スタート）
        count = 1
        embed = Embed(title="先攻・後攻の抽選を行います", description="抽選中...")
        await before_start.edit(embed=embed)
        random.shuffle(names)  # 抽選
        await sleep(1)

    # countが0 == nameの取得失敗 このifにかかったら絶対ここで終わらせる
    if count == 0 or count > 4:
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
            return "battle_error"
        if message.content == "cancel":
            await bot_channel.send("キャンセルしました。")
            return "battle_error"
        battle_status = await battle(message.content, client)
        return battle_status

    # 接続確認
    async def connection(voice_client: VoiceClient):
        if voice_client.is_connected() is False:
            try:
                await stage_channel.connect(reconnect=True)
                await chat.guild.me.edit(suppress=False)
            except Exception:  # このExceptionにかかったら絶対ここで終わらせる
                embed = Embed(
                    title="Error", description="接続が失われたため、タイマーを停止しました\n`battle timer failure due to lost connection`\n\n自動でバトル再開準備を行います\n`battle timer is rebooting automatically`", color=0xff0000)
                await bot_channel.send(embed=embed)
                await chat.send(embed=embed)
                await bot_channel.send(f"----------\n\n再開コマンド自動入力：{names[0]} vs {names[1]} Round{count}\n\n----------")
                battle_status = await battle(f"{names[0]} {names[1]} {count}", client)
                if battle_status == "battle_error":
                    return "battle_error"
                return "battle_skip"
            else:
                print("lost connection: auto reconnect done")
        return

    # タイマー
    async def timer(time: float, message: Message, voice_client: VoiceClient, count: int):
        battle_status = await connection(voice_client)
        if bool(battle_status):
            return battle_status

        def check(reaction, user):
            role_check = user.get_role(1096821566114902047)  # バトスタ運営
            return bool(role_check) and str(reaction.emoji) == '❌' and reaction.message == message
        try:
            _, _ = await client.wait_for('reaction_add', timeout=time, check=check)
        except asyncio.TimeoutError:
            pass
        else:  # このelseにかかったら絶対ここで終わらせる
            audio = PCMVolumeTransformer(FFmpegPCMAudio("timer_stop.mp3"))
            audio.read()
            try:
                voice_client.stop()
                chat.guild.voice_client.play(audio)
            except Exception:
                pass
            embed = Embed(title="Error",
                          description="問題が発生したため、タイマーを停止しました\n`battle timer failure due to an error`\n\n自動でバトル再開準備を行います\n`battle timer is rebooting automatically`", color=0xff0000)
            await bot_channel.send(embed=embed)
            await chat.send(embed=embed)
            await bot_channel.send(f"----------\n\n再開コマンド自動入力：{names[0]} vs {names[1]} Round{count}\n\n----------")
            battle_status = await battle(f"{names[0]} {names[1]} {count}", client)
            if battle_status == "battle_error":
                return "battle_error"
            return "battle_skip"

    ##############################
    # バトル開始前準備
    ##############################

    # vc接続
    voice_client = chat.guild.voice_client
    if voice_client is None:
        voice_client = await stage_channel.connect(reconnect=True)
    await chat.guild.me.edit(suppress=False)

    # ミュートしろ
    mute_right_now = f"{tari3210.mention}\nミュートしなさい!"
    for i in range(random.randint(1, 29)):
        mute_right_now += "!"

    # スタート音声準備
    random_start = random.randint(1, 3)
    audio = PCMVolumeTransformer(FFmpegPCMAudio(
        f"BattleStart_{random_start}.mp3"), volume=0.4)
    audio.read()

    # 開始前パネル
    embed = Embed(title=f"1️⃣ {names[0]} 🆚 {names[1]} 2️⃣",
                  description=f"1分・2ラウンドずつ\n`1 minute, 2 rounds each`\n\n> 1st: __**{names[0]}**__")
    embed.timestamp = datetime.now(JST)
    if len(names) == 2:  # 通常スタート時
        embed.description += "\n`（抽選で決定されました）`"
        await chat.send(f"{names[0]}さん\n{names[1]}さん\n\nステージのスピーカーになってください。\nやり方がわからない場合はチャット欄にてお知らせください。こちらから招待を送信します。")
    await chat.send(embed=embed)

    embed.description += "\n- ▶️ スタート\n- ❌ キャンセル"
    if last_match is False:  # 最終マッチでない場合スキップ可
        embed.description += "\n- ⏭️ このバトルをスキップ（最終マッチ後に自動追加されます）"
    elif last_match is True:  # 最終マッチの場合スキップ不可
        embed.description += "\n\n※最終マッチ（スキップしたバトルがある場合、この後開催されます）"
    await before_start.edit(embed=embed)

    # バトル開始ボタン
    await before_start.add_reaction("▶️")
    await before_start.add_reaction("❌")
    if last_match is False:  # 最終マッチでない場合スキップ可
        await before_start.add_reaction("⏭️")

    def check(reaction, user):
        stamps = ["▶️", "❌", "⏭️"]
        role_check = user.get_role(1096821566114902047)  # バトスタ運営
        return bool(role_check) and reaction.emoji in stamps and reaction.message == before_start

    reaction, _ = await client.wait_for('reaction_add', check=check)
    await before_start.clear_reactions()

    if reaction.emoji == "❌":  # s.startの自動スタート中止
        await before_start.delete()
        return "battle_error"
    if reaction.emoji == "⏭️":  # このバトルをスキップ（最終マッチ後に追加）
        await before_start.delete()
        return f"battle_reschedule {names[0]} vs {names[1]}"

    ##############################
    # いざ参らん
    ##############################

    # スタート音声再生
    chat.guild.voice_client.play(audio)

    # are you ready?
    embed = Embed(title="Are you ready??",
                  description=f"1️⃣ {names[0]} 🆚 {names[1]} 2️⃣", color=0x00ff00)
    sent_message = await bot_channel.send(embed=embed)
    await chat.send(embed=embed)
    await sent_message.add_reaction("❌")  # タイマー停止ボタン

    # 最初は4.8秒
    battle_status = await timer(4.8, sent_message, voice_client, count)
    if bool(battle_status):
        return battle_status

    # 4.8秒後ミュートしてるか確認
    if all([bool(tari3210.voice), tari3210.voice.self_mute is False, tari3210.voice.suppress is False]):
        await chat.send(mute_right_now)

    if random_start == 1:
        battle_status = await timer(4, sent_message, voice_client, count)
    else:
        battle_status = await timer(6, sent_message, voice_client, count)
    if bool(battle_status):
        return battle_status

    embed = Embed(title="🔥🔥 3, 2, 1, Beatbox! 🔥🔥", color=0xff0000)
    await sent_message.edit(embed=embed)
    await chat.send(embed=embed)
    battle_status = await timer(3, sent_message, voice_client, count)
    if bool(battle_status):
        return battle_status

    # タイマー
    while count <= 4:
        embed = Embed(
            title="1:00", description=f"Round{stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} 🆚 {names[1]}", color=0x00ff00)
        await sent_message.edit(embed=embed)
        await chat.send(embed=embed, delete_after=10)
        counter = 50
        color = 0x00ff00
        for i in range(5):
            # ラグ考慮のため9.9秒
            battle_status = await timer(9.9, sent_message, voice_client, count)
            if bool(battle_status):
                return battle_status
            embed = Embed(
                title=f"{counter}", description=f"Round{stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} 🆚 {names[1]}", color=color)
            await sent_message.edit(embed=embed)
            await chat.send(embed=embed, delete_after=5)
            counter -= 10
            if i == 1:
                color = 0xffff00
            if i == 3:
                color = 0xff0000

        # 50秒経過
        battle_status = await timer(4.9, sent_message, voice_client, count)
        if bool(battle_status):
            return battle_status
        embed = Embed(
            title="5", description=f"Round{stamps[count]}  **{names[1 - count % 2]}**\n\n{names[0]} 🆚 {names[1]}", color=color)
        await sent_message.edit(embed=embed)
        await chat.send(embed=embed, delete_after=5)
        battle_status = await timer(4.9, sent_message, voice_client, count)
        if bool(battle_status):
            return battle_status

        # 60秒経過
        if count <= 3:  # ここでスイッチ
            audio = PCMVolumeTransformer(FFmpegPCMAudio(
                f"round{count + 1}switch_{random.randint(1, 3)}.mp3"), volume=2)
            audio.read()
            chat.guild.voice_client.play(audio)
            embed = Embed(
                title="TIME!", description=f"Round{stamps[count + 1]}  **{names[count % 2]}**\nSWITCH!\n\n{names[0]} 🆚 {names[1]}")
            await sent_message.edit(embed=embed)
            await chat.send(embed=embed, delete_after=3)
            battle_status = await timer(3, sent_message, voice_client, count)
            if bool(battle_status):
                return battle_status
        count += 1

    # バトル終了
    audio = PCMVolumeTransformer(FFmpegPCMAudio(
        f"time_{random.randint(1, 2)}.mp3"), volume=0.5)
    audio.read()
    await sent_message.delete()
    embed = Embed(title="投票箱（集計は行いません）",
                  description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\n>>> BATTLE STADIUM\n毎週土曜21:30~ 開催中！", color=0x00bfff)
    embed.set_footer(text=f"bot開発者: {str(tari3210)}",
                     icon_url=tari3210.display_avatar.url)
    embed.timestamp = datetime.now(JST)

    # fuga
    if random.randint(1, 20) == 1:
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("time_fuga.mp3"), volume=0.4)
        audio.read()
        chat.guild.voice_client.play(audio)
        await sleep(7)
        poll = await bot_channel.send(f"{vc_role.mention}\nなあああああああああああああああああああああああああああああああああああああああああああああああああああああああああ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！", embed=embed)
        await poll.add_reaction("1⃣")
        await poll.add_reaction("2⃣")
        await poll.add_reaction("🦁")
        await chat.send("なああああああああああああああああああああああああああああああああああああ", embed=embed_chat_info)
        return

    # not fuga
    chat.guild.voice_client.play(audio)
    poll = await bot_channel.send(f"{vc_role.mention}\nmake some noise for the battle!\ncome on!!", embed=embed)
    await poll.add_reaction("1⃣")
    await poll.add_reaction("2⃣")
    await poll.add_reaction("🔥")
    audio = PCMVolumeTransformer(FFmpegPCMAudio(
        f"msn_{random.randint(1, 3)}.mp3"), volume=0.7)
    audio.read()
    await sleep(3.9)
    chat.guild.voice_client.play(audio)
    await chat.send("make some noise for the battle!\ncome on!!", embed=embed_chat_info)
    return


"""
s.start コマンド
"""


async def start(client: Client):
    # 初期設定
    bot_channel = client.get_channel(930447365536612353)  # bot
    stage_channel = client.get_channel(931462636019802123)  # ステージ
    chat = stage_channel
    pairing_channel = client.get_channel(930767329137143839)  # 対戦表
    entry_channel = client.get_channel(930446820839157820)  # 参加
    general = client.get_channel(864475338340171791)  # 全体チャット
    maiku_check = client.get_channel(1115986804026392627)  # maiku_check
    bs_role = chat.guild.get_role(930368130906218526)  # BATTLE STADIUM
    vc_role = chat.guild.get_role(935073171462307881)  # in a vc
    announce = chat.guild.get_channel(885462548055461898)  # お知らせ
    tari3210 = chat.guild.get_member(412082841829113877)
    scheduled_events = chat.guild.scheduled_events
    embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                            description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nBATTLEタイマー： {bot_channel.mention}\nマイクチェック： {maiku_check.mention}", color=0x00bfff)
    embed_maiku_check = Embed(
        title="事前マイクチェックをご利用ください",
        description=f"事前にマイク設定画面のスクショを提出して、botによるマイクチェックを受けてください\n\nマイクチェックチャンネルはこちら {maiku_check.mention}", color=0xffff00)
    await bot_channel.send("処理中...", delete_after=10)
    await chat.send("ただいま準備中...", embed=embed_chat_info)
    counter = 1
    counter2 = 0

    # イベントスタート
    try:
        for scheduled_event in scheduled_events:
            if scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.start()
                break
        await stage_channel.create_instance(topic="BATTLE STADIUM", send_notification=True)
    except Exception as e:
        print("event exception raised\n" + str(e))
        pass
    await general.send(f"【エキシビションBeatboxバトルイベント】\nバトルスタジアムを開始します！\nぜひご参加ください！観戦も大歓迎！\n{stage_channel.jump_url}", file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))

    # vc接続
    if chat.guild.voice_client is None:
        await stage_channel.connect(reconnect=True)
    await chat.guild.me.edit(suppress=False)

    # ロールメンバー削除
    if len(bs_role.members) >= 10:
        await bot_channel.send("処理に時間がかかっています。しばらくお待ちください。", delete_after=10)
        await chat.send("処理に時間がかかっています。しばらくお待ちください。", delete_after=10)
    await pairing_channel.purge()
    for member in bs_role.members:
        await member.remove_roles(bs_role)

    # エントリーボタン準備
    button = Button(label="Entry", style=ButtonStyle.primary, emoji="✅")
    embed_caution = Embed(title="【注意事項】",
                          description=f"- ノイズキャンセル設定に問題がある方が非常に増えています。\n必ず事前に {maiku_check.mention} にマイク設定画面のスクショを提出して、botによるマイクチェックを受けてください。\n\n- Discordの音声バグが発生した場合、バトルを中断し、途中のラウンドからバトルを再開することがあります。\n※音声バグ発生時の対応は状況によって異なります。ご了承ください。", color=0xffff00)

    async def button_callback(interaction: Interaction):  # エントリーボタン押されたときの処理
        await interaction.response.defer(ephemeral=True, thinking=False)
        role_check = interaction.user.get_role(
            930368130906218526)  # BATTLE STADIUM
        if bool(role_check):
            embed = Embed(title="受付済み entry already completed", color=0xff0000)
            await interaction.followup.send(embeds=[embed, embed_caution], ephemeral=True)
            return
        await interaction.user.add_roles(bs_role)
        embed = Embed(title="受付完了 entry completed", color=0x00ff00)
        await interaction.followup.send(embeds=[embed, embed_caution], ephemeral=True)
        # マイクチェックをしろ
        await maiku_check.send(f"{interaction.user.mention}\nこちらにて事前マイクチェックのご利用をお願いします", delete_after=5)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    embed = Embed(
        title="Entry", description="下のボタンを押してエントリー！\npress button to entry")

    # アナウンス準備
    audio = PCMVolumeTransformer(FFmpegPCMAudio("announce.mp3"))
    audio.read()

    # アナウンス開始・受付開始
    entry_button = await entry_channel.send(vc_role.mention, embed=embed, view=view)
    chat.guild.voice_client.play(audio)

    embed = Embed(
        title="受付開始", description=f"ただいまより参加受付を開始します。\n{entry_channel.mention}にてエントリーを行ってください。\nentry now accepting at {entry_channel.mention}", color=0x00bfff)
    await bot_channel.send(embed=embed)
    await chat.send(embed=embed)
    await entry_channel.send(f"エントリー後に、botによるマイクチェックを受けてください。\n{maiku_check.mention}", delete_after=60)

    # 1分時間をつぶす
    await sleep(10)
    await chat.send(embed=embed_maiku_check)
    await sleep(10)
    entry_button2 = await chat.send("このボタンからもエントリーできます", embed=embed, view=view)
    await sleep(10)
    embed = Embed(title="あと30秒で締め切ります", color=0xffff00)
    await bot_channel.send(embed=embed)
    await chat.send(embed=embed_chat_info)
    await sleep(10)
    await entry_channel.send(f"{vc_role.mention}\nボタンを押してエントリー！\npress button to entry", delete_after=20)
    await chat.send(embed=embed_maiku_check)
    await sleep(10)
    embed = Embed(title="締め切り10秒前", color=0xff0000)
    await bot_channel.send(embed=embed)
    await sleep(10)

    # 〆
    await entry_button.delete()
    await entry_button2.delete()
    await bot_channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
    await chat.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")

    # 抽選処理
    playerlist_m = bs_role.members
    if len(playerlist_m) < 2:
        embed = Embed(title="Error", description="参加者が不足しています。",
                      color=0xff0000)
        await bot_channel.send(embed=embed)
        await chat.send(embed=embed)
        return
    random.shuffle(playerlist_m)
    playerlist = [member.display_name.replace("`", "").replace(
        " ", "-").replace("　", "-") for member in playerlist_m]

    # 奇数処理
    if len(playerlist) % 2 == 1:
        double_player = playerlist_m[0].mention
        embed = Embed(title="参加人数が奇数でした",
                      description=f"{playerlist[0]}さんの対戦が2回行われます\n\n※あと1人参加者が追加された場合、{playerlist[0]}さんと交代になります。", color=0x00bfff)
        await bot_channel.send(embed=embed)
        await pairing_channel.send(f"参加人数が奇数でした。\n\nあと1人参加者が追加された場合、{double_player}さん（最終マッチ）と交代になります。")

    # 抽選結果書き出し
    embed_pairing = Embed(
        title="対戦カード 抽選結果", description="先攻・後攻は、バトル直前に抽選を行い決定します", color=0xff9900)
    embed_pairing.set_footer(
        text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
    embed_pairing.timestamp = datetime.now(JST)
    while counter2 + 2 <= len(playerlist):
        embed_pairing.add_field(
            name=f"Match{counter}", value=f"{playerlist[counter2]} 🆚 {playerlist[counter2 + 1]}", inline=False)
        counter += 1
        counter2 += 2
    if len(playerlist) % 2 == 1:  # 奇数の場合Match1参加者にもう一度やってもらう
        embed_pairing.add_field(
            name=f"Match{counter}", value=f"{playerlist[-1]} 🆚 ※{playerlist[0]}\n※{playerlist[0]}さんは交代の可能性有", inline=False)

    # 抽選結果送信
    await bot_channel.send(embed=embed_pairing)
    await pairing_channel.send(embed=embed_pairing)
    await chat.send(embed=embed_pairing)

    # マ イ ク チ ェ ッ ク を し ろ
    await maiku_check.send(f"{bs_role.mention}", embed=embed_maiku_check, delete_after=20)

    ##############################
    # バトル実行関数
    ##############################

    rescheduled_match = []  # スキップしたマッチ

    async def execute_battle(names, client):
        battle_status = await battle(names, client)
        if battle_status == "battle_error":  # 異常終了
            embed = Embed(
                title="自動入力中止",
                description="s.battleコマンド自動入力を中止します\n`s.battle [名前1] [名前2]` と入力してください",
                color=0xff0000)
            await bot_channel.send(embed=embed)
            return "battle_error"

        if battle_status.startswith("battle_reschedule"):  # バトルスキップ（最終マッチに追加する場合）
            embed = Embed(
                title=f"{names} をスキップします",
                description=f"{names} は最終マッチの後に行います",
                color=0x00bfff)
            await bot_channel.send(embed=embed)
            await chat.send(embed=embed)
            rescheduled_match.append(
                battle_status.replace("battle_reschedule ", ""))
            return "battle_skip"
        return

    # バトルループ
    for i in range(0, len(playerlist), 2):
        await sleep(3)
        try:
            battle_status = await execute_battle(f"{playerlist[i]} {playerlist[i + 1]}", client)
        except IndexError:  # 参加者数が奇数のとき発生
            embed = Embed(
                title="最終マッチを行います", description=f"参加者数が奇数だったため、これより\n{playerlist[-1]} vs `{playerlist[0]}(2回目)`\nを行う予定です。\n{playerlist[-1]} さんの対戦相手を変更しますか？\n\n⭕ 変更する\n❌ `{playerlist[-1]} vs {playerlist[0]} を行う`", color=0xffff00)
            confirm_msg = await bot_channel.send(embed=embed)
            await confirm_msg.add_reaction("⭕")
            await confirm_msg.add_reaction("❌")

            def check(reaction, user):
                stamps = ["⭕", "❌"]
                role_check = user.get_role(1096821566114902047)  # バトスタ運営
                return bool(role_check) and reaction.emoji in stamps and reaction.message == confirm_msg
            reaction, _ = await client.wait_for('reaction_add', check=check)
            await confirm_msg.clear_reactions()

            if reaction.emoji == "⭕":  # 対戦相手変更
                embed = Embed(
                    title="対戦相手を入力してください", description=f"`{playerlist[-1]} vs ???`\n\n`cancelと入力するとキャンセルできます`\n↓このチャットに入力↓")
                await bot_channel.send(embed=embed)

                def check(message):
                    role_check = message.author.get_role(
                        1096821566114902047)  # バトスタ運営
                    return message.channel == bot_channel and bool(role_check)
                try:
                    message = await client.wait_for('message', timeout=600, check=check)
                except asyncio.TimeoutError:
                    await bot_channel.send("Error: timeout")
                    return
                if message.content == "cancel":
                    await bot_channel.send("キャンセルしました。")
                    return
                last_player = message.content.replace(
                    "`", "").replace(" ", "-")

            if reaction.emoji == "❌":  # 変更しない
                last_player = playerlist[0]

            # 最終マッチ開始
            battle_status = await execute_battle(f"{playerlist[-1]} {last_player} last", client)

        if battle_status == "battle_error":  # 異常終了
            return "battle_error"

    ##############################
    # スキップしたマッチを開催
    # whileでひたすら回す
    ##############################

    while len(rescheduled_match) > 0:
        current_matches = rescheduled_match.deepcopy()
        embed = Embed(
            title="スキップされたバトル",
            description="これより、スキップされたバトルを開催します\n開催するバトルは以下の通りです",
            color=0x00bfff)
        for names in current_matches:
            embed.description += f"\n- {names}"
        await bot_channel.send(embed=embed)
        await chat.send(embed=embed)
        await pairing_channel.send(embed=embed)

        for names in current_matches:
            battle_status = await execute_battle(names, client)
            rescheduled_match.remove(names)  # 1つ終わったら削除

            if battle_status == "battle_error":  # 異常終了
                return "battle_error"

    # すべてのバトル終了
    embed = Embed(title="すべてのバトルが終了しました all battles are over",
                  description="ご参加ありがとうございました！\nmake some noise for all of amazing performance!!",
                  color=0x00bfff)
    await bot_channel.send(embed=embed)
    await chat.send(embed=embed)
    dt_now = datetime.now(JST)

    # 終了時刻が22:30以前
    if dt_now.time() < datetime.time(hour=22, minute=30):
        embed = Embed(title="BATTLE STADIUM エントリー再受付 開始ボタン",
                      description="- ▶️ エントリー再受付開始\n- ❌ このメッセージを削除\n- 👋 バトスタ終了")
        battle_stadium_restart = await bot_channel.send(embed=embed)
        await battle_stadium_restart.add_reaction("▶️")
        await battle_stadium_restart.add_reaction("❌")
        await battle_stadium_restart.add_reaction("👋")

        def check(reaction, user):
            stamps = ["▶️", "❌", "👋"]
            role_check = user.get_role(1096821566114902047)  # バトスタ運営
            return bool(role_check) and reaction.emoji in stamps and reaction.message == battle_stadium_restart

        try:
            reaction, _ = await client.wait_for('reaction_add', check=check, timeout=600)
            await battle_stadium_restart.delete()
        except TimeoutError:  # 10分経過ならさよなら
            await battle_stadium_restart.delete()
            return
        if reaction.emoji == "❌":  # ❌ならさよなら
            return
        if reaction.emoji == "▶️":
            await start(client)  # バトスタ再受付開始
            return

    # 終了時刻が22:30以降 or エントリー再受付しない
    # バトスタ終了ボタン
    embed = Embed(title="BATTLE STADIUMを終了しますか？",
                  description="- 👋 バトスタ終了\n- ❌ このメッセージを削除")
    battle_stadium_end = await bot_channel.send(embed=embed)
    await battle_stadium_end.add_reaction("👋")
    await battle_stadium_end.add_reaction("❌")

    def check(reaction, user):
        stamps = ["👋", "❌"]
        role_check = user.get_role(1096821566114902047)  # バトスタ運営
        return bool(role_check) and reaction.emoji in stamps and reaction.message == battle_stadium_end

    try:
        reaction, _ = await client.wait_for('reaction_add', check=check, timeout=600)
        await battle_stadium_end.delete()
    except TimeoutError:  # 10分経過なら処理終了
        await battle_stadium_end.delete()
        return
    if reaction.emoji == "❌":  # ❌ならさよなら
        return

    # ステージインスタンス終了
    scheduled_events = message.guild.scheduled_events
    for scheduled_event in scheduled_events:
        if scheduled_event.status == EventStatus.active and scheduled_event.name == "BATTLE STADIUM":
            await scheduled_event.end()
    try:
        instance = await stage_channel.fetch_instance()
    except Exception:
        pass
    else:
        await instance.delete()

    # 次のバトスタ設定 datetimeだけ用意
    weekday = dt_now.weekday()  # 今日の曜日を取得
    days_to_saturday = (5 - weekday) % 7  # 土曜日までの日数を計算
    dt_next = dt_now + timedelta(days=days_to_saturday + 14)  # 2週間後の土曜日を計算
    dt_next_start = dt_next.replace(hour=21, minute=30, second=0)  # 21:30に設定
    dt_next_end = dt_next.replace(hour=22, minute=30, second=0)  # 22:30に設定

    # 次のバトスタ設定ボタン
    embed = Embed(title="次のバトスタ設定",
                  description=f"次のバトスタは\n**{dt_next_start.strftime('%m/%d 21:30~')}**\nの予定です\n\nイベントを設定しますか？",
                  color=0x00bfff)
    next_battle_stadium = await bot_channel.send(tari3210.mention, embed=embed)
    await next_battle_stadium.add_reaction("⭕")
    await next_battle_stadium.add_reaction("❌")

    def check(reaction, user):
        stamps = ["⭕", "❌"]
        role_check = user.get_role(1096821566114902047)  # バトスタ運営
        return bool(role_check) and reaction.emoji in stamps and reaction.message == next_battle_stadium

    try:
        reaction, _ = await client.wait_for('reaction_add', check=check, timeout=600)
        await next_battle_stadium.delete()
    except TimeoutError:
        await next_battle_stadium.delete()
    else:
        if reaction.emoji == "⭕":  # 2週間後のバトスタイベントを設定
            # 以下s.bsと同じ処理
            event = await message.guild.create_scheduled_event(
                name="BATTLE STADIUM",
                description="【エキシビションBeatboxバトルイベント】\n今週もやります！いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。", start_time=dt_next_start,
                end_time=dt_next_end,
                channel=stage_channel,
                privacy_level=PrivacyLevel.guild_only)
            await bot_channel.send(f"イベント設定完了しました\n{event.url}")
            await announce.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
            await announce.send(event.url)
            await chat.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
            await chat.send(event.url)

    # ここの後片付けは時間がかかるので最後にやる
    await pairing_channel.purge()
    for member in bs_role.members:
        await member.remove_roles(bs_role)
    return
