import asyncio
import datetime
import random
from asyncio import sleep

import discord
from discord import (ChannelType, Client, Embed, EventStatus, FFmpegPCMAudio,
                     File, Intents, Member, Message, PCMVolumeTransformer,
                     PrivacyLevel, VoiceState)
from discord.errors import ClientException

from battle_stadium import battle, start

intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc
        if bool(before.channel) and after.channel is None:
            await member.remove_roles(vc_role)
        elif before.channel != after.channel and bool(after.channel):
            embed = Embed(title="BEATBOXをもっと楽しむために",
                          description="", color=0x0081f0)
            embed.add_field(name=f"Let's show your 💜❤💙💚 with `{member.display_name}`!",
                            value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。")
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森", icon_url=member.guild.icon.url)
            if after.channel.id == 886099822770290748:  # リアタイ部屋
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", embed=embed, delete_after=60)
            else:
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", delete_after=60)
            await member.add_roles(vc_role)
    except Exception:
        return


@client.event
async def on_member_join(member: Member):
    channel = client.get_channel(864475338340171791)  # 全体チャット
    await sleep(1)
    embed_discord = Embed(
        title="Discordの使い方", description="https://note.com/me1o_crew/n/nf2971acd1f1a")
    embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    events = channel.guild.scheduled_events
    events_exist = []
    for event in events:
        if event.status in [EventStatus.scheduled, EventStatus.active]:
            events_exist.append(event)
    if bool(events_exist) is False:
        return
    closest_event = events_exist[0]
    for event in events_exist:
        if event.start_time < closest_event.start_time:
            closest_event = event
    await sleep(1)
    await channel.send(closest_event.url)


@client.event
async def on_message(message: Message):
    if not message.content.startswith("s."):
        if any([message.author.bot, "https://gbbinfo-jpn.jimdofree.com/" in message.content, message.channel.id == 930767329137143839]):  # バトスタ対戦表
            return
        if message.channel.id == 930447365536612353:  # バトスタbot
            if message.content.startswith("l."):
                return
            await message.delete(delay=1)
            return
        for word in ["💜❤💙💚", "brez", "ぶれず", "ブレズ", "愛", "sar", "oras", "かわいい", "カワイイ"]:
            if word in message.content.lower():
                for stamp in ["💜", "❤", "💙", "💚"]:
                    await message.add_reaction(stamp)
        embed = Embed(title="GBBの最新情報はこちら", description=">>> 以下のサイトにお探しの情報がない場合、\n__**未発表 もしくは 未定（そもそも決定すらしていない）**__\n可能性が非常に高いです。", color=0xF0632F)
        embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                        value="https://gbbinfo-jpn.jimdofree.com/")
        embed.add_field(name="swissbeatbox 公式instagram",
                        value="https://www.instagram.com/swissbeatbox/")
        if "m!wc" in message.content.lower():
            await message.channel.send(embed=embed)
            await message.channel.send("[GBB 2023 Wildcard結果・出場者一覧 はこちら](https://gbbinfo-jpn.jimdofree.com/20230222/)")
        if message.channel.type == ChannelType.text:
            emoji = random.choice(message.guild.emojis)
            await message.add_reaction(emoji)
            for word in ["gbb", "wildcard", "ワイカ", "ワイルドカード", "結果", "出場", "通過", "チケット", "ルール", "審査員", "ジャッジ", "日本人", "colaps"]:
                if word in message.content.lower():
                    if any(["?" in message.content, "？" in message.content]):
                        await message.reply("[GBBINFO-JPN 日本非公式情報サイト](https://gbbinfo-jpn.jimdofree.com/)")
                        await message.reply(embed=embed)
                    else:
                        await message.channel.send(embed=embed)
                    break
            await sleep(3600)
            try:
                await message.remove_reaction(emoji, message.guild.me)
            except Exception:
                pass

    if message.channel.id == 930839018671837184:  # バトスタチャット
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    if message.content == "s.join":
        await message.delete(delay=1)
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except ClientException:
            await message.channel.send("既に接続しています。\nチャンネルを移動させたい場合、一度切断してからもう一度お試しください。")
            return
        else:
            await message.channel.send("接続しました。")
            return

    if message.content == "s.leave":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
        return

    if message.content == "s.p time" or message.content == "s.time":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 3)
        ran_audio = {1: "time.mp3", 2: "time_2.mp3", 3: "time_3.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3",
                     3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.c") and "s.c90" not in message.content and "s.cancel" not in message.content and "s.check" not in message.content:
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        voice_client = message.guild.voice_client
        names = [(j) for j in message.content.replace('s.c', '').split()]
        if len(names) == 0:
            await message.delete(delay=1)
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            embed = Embed(title="3, 2, 1, Beatbox!")
            sent_message = await message.channel.send(embed=embed)
            message.guild.voice_client.play(audio)
            await sleep(7)
            connect = voice_client.is_connected()
            if connect is False:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                await sent_message.delete()
                return
            embed = Embed(title="1:00", color=0x00ff00)
            await sent_message.edit(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = Embed(title=f"{counter}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                connect = voice_client.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                    await sent_message.delete()
                    return
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(9.9)
            embed = Embed(title="TIME!")
            await sent_message.edit(embed=embed, delete_after=10)
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = PCMVolumeTransformer(
                FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            return

        count = 1
        if len(names) == 3:
            try:
                count = int(names[2])
            except ValueError:
                pass
            if 2 <= count <= 4:
                embed = Embed(
                    title="再開コマンド", description=f"Round{count}から再開します。\n\n※意図していない場合、`s.leave`と入力してbotを停止した後、再度入力してください。")
                await message.channel.send(embed=embed, delete_after=60)
                del names[2]
        while len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。\n\n`cancelと入力するとキャンセルできます`\nもう一度入力してください：", delete_after=60)

            def check(m):
                return m.channel == message.channel and m.author == message.author

            try:
                msg2 = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Error: timeout", delete_after=5)
                return
            if msg2.content.startswith("s.c"):
                return
            await msg2.delete(delay=5)
            if msg2.content == "cancel":
                await message.channel.send("キャンセルしました。", delete_after=5)
                return
            names = [(j)
                     for j in msg2.content.replace('s.c', '').split()]
        embed = Embed(title=f"1️⃣ {names[0]} vs {names[1]} 2️⃣",
                      description="1分・2ラウンドずつ\n1 minute, 2 rounds each\n\n▶️を押してスタート")
        before_start = await message.channel.send(embed=embed)
        await before_start.add_reaction("▶️")
        await before_start.add_reaction("❌")
        stamps = ["▶️", "❌"]

        def check(reaction, user):
            return user == message.author and reaction.emoji in stamps and reaction.message == before_start

        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:
            await message.channel.send("Error: timeout", delete_after=5)
            await before_start.delete()
            return
        if reaction.emoji == "❌":
            await before_start.delete()
            return
        if count % 2 == 0:
            names.reverse()
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        embed = Embed(title="3, 2, 1, Beatbox!")
        sent_message = await message.channel.send(embed=embed)
        message.guild.voice_client.play(audio)
        await sleep(7)
        await before_start.delete()
        while count <= 4:
            embed = Embed(
                title="1:00", description=f"Round{count} {names[0]}", color=0x00ff00)
            await sent_message.edit(embed=embed)
            timeout = 9.9
            counter = 50
            color = 0x00ff00
            connect = voice_client.is_connected()
            if connect is False:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                return
            while True:
                def check(reaction, user):
                    admin = user.get_role(904368977092964352)  # ビト森杯運営
                    return bool(admin) and reaction.emoji == '⏭️' and reaction.message == sent_message
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    connect = voice_client.is_connected()
                    if connect is False:
                        await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection", delete_after=5)
                        await sent_message.delete()
                        return
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました", delete_after=5)
                        await sent_message.delete()
                        return
                    embed = Embed(
                        title=f"{counter}", description=f"Round{count} {names[0]}", color=color)
                    await sent_message.edit(embed=embed)
                    counter -= 10
                    if counter == 30:
                        color = 0xffff00
                    elif counter == 10:
                        color = 0xff0000
                    elif counter == 0:
                        color = 0x000000
                        await sent_message.add_reaction("⏭️")
                    elif counter == -10:
                        timeout = 60
                        if count == 4:
                            await sent_message.clear_reactions()
                            break
                else:
                    await sent_message.clear_reactions()
                    break
            names.reverse()
            count += 1
        embed = Embed(
            title="TIME!", description="make some noise for the battle!!")
        await sent_message.edit(embed=embed)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        await sleep(3)
        embed = Embed(
            title="オーディエンス投票受付中", description="YouTube投票機能を利用して集計します")
        embed.add_field(name="※投票できないときは",
                        value="アプリの再起動をお試しください", inline=False)
        await sent_message.edit(embed=embed, delete_after=20)
        return

    if message.content.startswith("s.bj"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [j for j in message.content.split()]
        names.remove("s.bj")
        round_count = 1
        if len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        await message.channel.send("3, 2, 1, Beatbox!", delete_after=10)
        message.guild.voice_client.play(audio)
        await sleep(7)
        embed = Embed(
            title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        while round_count < 5:
            timeout = 10
            counter = 80
            color = 0x00ff00
            while True:
                def check(reaction, user):
                    return user.bot is False and reaction.emoji == '⏭️'
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました")
                        return
                    embed = Embed(
                        title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
                    await sent_message.edit(embed=embed)
                    counter -= 10
                    if counter == 30:
                        color = 0xffff00
                    elif counter == 10:
                        color = 0xff0000
                    elif counter == 0:
                        color = 0x000000
                        await sent_message.add_reaction("⏭️")
                    elif counter == -10:
                        timeout = 30
                        if round_count == 4:
                            embed = Embed(
                                title="0", description=f"Round4 {names[0]}", color=color)
                            await sent_message.edit(embed=embed)
                            break
                else:
                    break
            embed = Embed(title="TIME!")
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            names.reverse()
            round_count += 1
            if round_count < 5:
                await message.channel.send("SWITCH!", delete_after=5)
                embed = Embed(
                    title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
                sent_message = await message.channel.send(embed=embed)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = PCMVolumeTransformer(
            FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.c90":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        embed = Embed(title="90", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        counter = 80
        color = 0x00ff00
        for i in range(8):
            await sleep(9.9)
            embed = Embed(title=f"{counter}", color=color)
            await sent_message.edit(embed=embed)
            counter -= 10
            if i == 4:
                color = 0xffff00
            elif i == 6:
                color = 0xff0000
        await sleep(9.9)
        embed = Embed(title="TIME!")
        await sent_message.edit(embed=embed)
        await sent_message.delete(delay=5)
        return

    if message.content.startswith("s.battle"):
        await battle(message.content, client)
        return

    if message.content == "s.start":
        await start(client)
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="BATTLE STADIUM")
        except Exception:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except ClientException:
            pass
        me = message.guild.me
        await me.edit(suppress=False)
        return

    if message.content == "s.end":
        await message.delete(delay=1)
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        bs_role = message.guild.get_role(930368130906218526)  # BATTLE STADIUM
        stage = client.get_channel(931462636019802123)  # ステージ
        scheduled_events = message.guild.scheduled_events
        for scheduled_event in scheduled_events:
            if scheduled_event.status == EventStatus.active and scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.end()
        try:
            instance = await stage.fetch_instance()
        except Exception:
            pass
        else:
            await instance.delete()
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        return

    if message.content.startswith("s.bs"):
        general = message.guild.get_channel(864475338340171791)  # 全体チャット
        announce = message.guild.get_channel(885462548055461898)  # お知らせ
        await message.delete(delay=1)
        JST = datetime.timezone(datetime.timedelta(hours=9))
        dt_now = datetime.datetime.now(JST)
        sat = datetime.timedelta(days=6 - int(dt_now.strftime("%w")))
        start_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 21, 30, 0, 0, JST) + sat
        end_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 22, 30, 0, 0, JST) + sat
        stage = client.get_channel(931462636019802123)  # BATTLE STADIUM
        event = await message.guild.create_scheduled_event(
            name="BATTLE STADIUM",
            description="今週もやります！\nこのイベントの趣旨は「とにかくBeatboxバトルをすること」です。いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。",
            start_time=start_time,
            end_time=end_time,
            channel=stage,
            privacy_level=PrivacyLevel.guild_only)
        await announce.send(file=File("battle_stadium.gif"))
        await announce.send(event.url)
        await general.send(file=File("battle_stadium.gif"))
        await general.send(event.url)
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
