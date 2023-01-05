import asyncio
import datetime
import random
from asyncio import sleep

import discord
from discord import Embed
from discord.ui import Button, View

intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = discord.Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")


@client.event
async def on_voice_state_update(member, before, after):
    vc_role = member.guild.get_role(935073171462307881)  # in a vc
    if all([before.channel is None, bool(after.channel)]):
        try:
            await member.add_roles(vc_role)
        except Exception:
            pass
        if member.id == 412082841829113877:  # tari3210
            return
        try:
            await after.channel.send(f"{member.mention}\nチャットはこちら\nchat is here", delete_after=60)
        except Exception:
            return
    if bool(before.channel) and after.channel is None:
        try:
            await member.remove_roles(vc_role)
        except Exception:
            pass


@client.event
async def on_message(message):
    if not message.content.startswith("s."):
        if message.author.bot:
            return
        # バトスタbot, バトスタ対戦表
        if message.channel.id in [930447365536612353, 930767329137143839]:
            await message.delete(delay=1)
            return
        if "m!judge" in message.content:
            embed = Embed(title="GBB 2023 TOKYO の最新情報はこちら", color=0xF0632F)
            embed.add_field(name="GBBINFO-JPN",
                            value="https://gbbinfo-jpn.jimdofree.com/")
            embed.add_field(name="swissbeatbox 公式インスタグラム",
                            value="https://www.instagram.com/swissbeatbox/")
            file = discord.File("fotor_2023-1-5_23_8_44.png")
            await message.channel.send(embed=embed, file=file)
        elif "gbb" in message.content.lower() and any(["?" in message.content, "？" in message.content]):
            embed = Embed(title="GBB 2023 TOKYO の最新情報はこちら", color=0xF0632F)
            embed.add_field(name="GBBINFO-JPN",
                            value="https://gbbinfo-jpn.jimdofree.com/")
            embed.add_field(name="swissbeatbox 公式インスタグラム",
                            value="https://www.instagram.com/swissbeatbox/")
            await message.reply(embed=embed)
        if message.channel.type == discord.ChannelType.text:
            emoji = random.choice(message.guild.emojis)
            await message.add_reaction(emoji)
            await sleep(3600)
            try:
                await message.remove_reaction(emoji, message.guild.me)
            except Exception:
                pass
            return

    if message.channel.id == 930839018671837184:  # バトスタチャット
        return

    if message.content == "s.test":
        await message.channel.send(f"Make Some Noise! (Server): {client.latency}")
        return

    if message.content == "s.join":
        await message.delete(delay=1)
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except discord.errors.ClientException:
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
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3",
                     3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.c") and "s.c90" not in message.content and "s.cancel" not in message.content and "s.check" not in message.content:
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        VoiceClient = message.guild.voice_client
        names = [(j) for j in message.content.replace('s.c', '').split()]
        if len(names) == 0:
            await message.delete(delay=1)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            embed = Embed(title="3, 2, 1, Beatbox!")
            sent_message = await message.channel.send(embed=embed)
            message.guild.voice_client.play(audio)
            await sleep(7)
            connect = VoiceClient.is_connected()
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
                connect = VoiceClient.is_connected()
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
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
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
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
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
            connect = VoiceClient.is_connected()
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
                    connect = VoiceClient.is_connected()
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
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
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
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
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
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
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
        chat = client.get_channel(930839018671837184)  # バトスタチャット
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        vc_role = message.guild.get_role(935073171462307881)  # in a vc
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        entry_channel = client.get_channel(930446820839157820)  # 参加
        embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                                description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nbattleタイマー： {message.channel.mention}", color=0x00bfff)
        await chat.send(embed=embed_chat_info)
        names = message.content.replace(
            " vs", "").replace('s.battle', '').split()
        count = 1
        if len(names) == 3:
            try:
                count = int(names[2])
            except ValueError:
                pass
            if 2 <= count <= 4:
                embed = Embed(
                    title="再開コマンド", description=f"Round{count}から再開します。\n\n※意図していない場合、`s.leave`と入力してbotを停止した後、再度入力してください。")
                await message.channel.send(embed=embed)
                del names[2]
        while len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。\n\n`cancelと入力するとキャンセルできます`\nもう一度入力してください：")

            def check(m):
                return m.channel == message.channel and m.author == message.author

            try:
                msg2 = await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send("Error: timeout")
                return
            if msg2.content == "cancel":
                await message.channel.send("キャンセルしました。")
                return
            if msg2.content.startswith("s.battle"):
                return
            names = msg2.content.replace(
                's.battle', '').replace(" vs", "").split()
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
            await before_start.clear_reactions()
            await before_start.reply("Error: timeout")
            return
        await before_start.clear_reactions()
        if reaction.emoji == "❌":
            await before_start.delete()
            return
        embed = Embed(title="Are you ready??")
        sent_message = await message.channel.send(embed=embed)
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        VoiceClient = message.guild.voice_client
        me = message.guild.me
        try:
            await me.edit(suppress=False)
        except AttributeError:
            pass
        random_start = random.randint(1, 3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"BattleStart_{random_start}.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        if random_start == 1:
            await sleep(9)
        else:
            await sleep(11)
        connect = VoiceClient.is_connected()
        if connect is False:
            await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
            return
        embed = Embed(title="3, 2, 1, Beatbox!")
        await sent_message.edit(embed=embed)
        await sleep(3)
        while count <= 4:
            embed = Embed(
                title="1:00", description=f"Round{count} {names[1 - count % 2]}\n\n{names[0]} vs {names[1]}", color=0x00ff00)
            await sent_message.edit(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = Embed(
                    title=f"{counter}", description=f"Round{count} {names[1 - count % 2]}\n\n{names[0]} vs {names[1]}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(4.9)
            embed = Embed(
                title="5", description=f"Round{count} {names[1 - count % 2]}\n\n{names[0]} vs {names[1]}", color=color)
            await sent_message.edit(embed=embed)
            await sleep(4.9)
            if count <= 3:
                audio = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(f"round{count + 1}switch_{random.randint(1, 3)}.mp3"))
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                message.guild.voice_client.play(audio)
                embed = Embed(
                    title="TIME!", description=f"Round{count + 1} {names[count % 2]}\nSWITCH!\n\n{names[0]} vs {names[1]}")
                await sent_message.edit(embed=embed)
                await sleep(3)
            count += 1
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"time_{random.randint(1, 2)}.mp3"), volume=0.3)
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        await sent_message.delete()
        tari3210 = message.guild.get_member(412082841829113877)
        if random.randint(1, 20) == 1:
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time_fuga.mp3"), volume=0.4)
            message.guild.voice_client.play(audio)
            embed = Embed(
                title="投票箱", description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
            embed.set_footer(
                text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
            await sleep(7)
            poll = await message.channel.send(f"{vc_role.mention}\nなあああああああああああああああああああああああああああああああああああああああああああああああああああああああああ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！", embed=embed)
            await poll.add_reaction("1⃣")
            await poll.add_reaction("2⃣")
            await poll.add_reaction("🦁")
            await chat.send(embed=embed_chat_info)
            return
        message.guild.voice_client.play(audio)
        embed = Embed(
            title="投票箱", description=f"1️⃣ {names[0]}\n2️⃣ {names[1]}\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。")
        embed.set_footer(
            text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
        poll = await message.channel.send(f"{vc_role.mention}\nmake some noise for the battle!\ncome on!!", embed=embed)
        await poll.add_reaction("1⃣")
        await poll.add_reaction("2⃣")
        await poll.add_reaction("🔥")
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"msn_{random.randint(1, 3)}.mp3"), volume=0.4)
        await sleep(4.5)
        message.guild.voice_client.play(audio)
        await chat.send(embed=embed_chat_info)
        return

    if message.content == "s.start":
        await message.channel.send("処理中...")
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        vc_role = message.guild.get_role(935073171462307881)  # in a vc
        bbx_mic = client.get_channel(931781522808262756)  # bbxマイク設定
        chat = client.get_channel(930839018671837184)  # バトスタチャット
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        bs_role = message.guild.get_role(930368130906218526)  # BATTLE STADIUM
        entry_channel = client.get_channel(930446820839157820)  # 参加
        scheduled_events = message.guild.scheduled_events
        embed_chat_info = Embed(title="チャット欄はこちら chat is here",
                                description=f"対戦表： {pairing_channel.mention}\nエントリー： {entry_channel.mention}\nbattleタイマー： {message.channel.mention}", color=0x00bfff)
        await chat.send(vc_role.mention, embed=embed_chat_info)
        try:
            for scheduled_event in scheduled_events:
                if scheduled_event.name == "BATTLE STADIUM":
                    await scheduled_event.start()
                    break
            await stage_channel.create_instance(topic="BATTLE STADIUM", send_notification=True)
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        await message.guild.me.edit(suppress=False)
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        button = Button(
            label="Entry", style=discord.ButtonStyle.primary, emoji="✅")

        async def button_callback(interaction):
            await interaction.response.defer(ephemeral=True, invisible=False)
            await interaction.user.add_roles(bs_role)
            embed = Embed(title="受付完了 entry completed",
                          description="※バトルを始める際、speakerになった後、ミュート以外画面操作を一切行わないでください\n\nDiscordバグにより音声が一切入らなくなります")
            await message.channel.send(f"エントリー完了：{interaction.user.display_name}", delete_after=3)
            await interaction.followup.send(embed=embed, ephemeral=True)

        button.callback = button_callback
        view = View()
        view.add_item(button)
        embed = Embed(
            title="Entry", description="下のボタンを押してエントリー！\npress button to entry")
        entry_button = await entry_channel.send(vc_role.mention, embed=embed, view=view)
        entry_button2 = await chat.send("このボタンからもエントリーできます", embed=embed, view=view)
        embed = Embed(
            title="受付開始", description=f"ただいまより参加受付を開始します。\n{entry_channel.mention}にてエントリーを行ってください。\nentry now accepting at {entry_channel.mention}", color=0x00bfff)
        await message.channel.send(embed=embed)
        await entry_channel.send(f"エントリー後に、 {bbx_mic.mention} を確認して、マイク設定を行ってください。", delete_after=60)
        await sleep(30)
        embed = Embed(title="あと30秒で締め切ります", color=0xffff00)
        await message.channel.send(embed=embed)
        await chat.send(embed=embed_chat_info)
        await entry_channel.send(f"{vc_role.mention}\nボタンを押してエントリー！\npress button to entry", delete_after=30)
        await sleep(20)
        embed = Embed(title="締め切り10秒前", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        await entry_button.delete()
        await entry_button2.delete()
        await message.channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
        playerlist = [member.display_name.replace(
            "`", "").replace(" ", "-") for member in bs_role.members]
        if len(playerlist) < 2:
            embed = Embed(
                title="Error", description="参加者が不足しています。", color=0xff0000)
            await message.channel.send(embed=embed)
            return
        random.shuffle(playerlist)
        counter = 1
        counter2 = 0
        embed = Embed(title="抽選結果", color=0xff9900)
        while counter2 + 2 <= len(playerlist):
            embed.add_field(
                name=f"Match{counter}", value=f"1️⃣ {playerlist[counter2]} vs {playerlist[counter2 + 1]} 2️⃣", inline=False)
            counter += 1
            counter2 += 2
        if len(playerlist) % 2 == 1:
            double_pl = message.guild.get_member_named(playerlist[0])
            if double_pl is None:
                double_pl = playerlist[0]
            else:
                double_pl = double_pl.mention
            await message.channel.send(f"----------------------------------------\n\n参加人数が奇数でした。\n{playerlist[0]}さんの対戦が2回行われます。")
            await pairing_channel.send(f"参加人数が奇数でした。\n{double_pl}さんの対戦が2回行われます。")
            await chat.send("参加人数が奇数でした。\nあと1人参加できます。ご希望の方はこのチャットにご記入ください。")
            embed.add_field(
                name=f"Match{counter}", value=f"1️⃣ {playerlist[-1]} vs {playerlist[0]} 2️⃣", inline=False)
        tari3210 = message.guild.get_member(412082841829113877)
        embed.set_footer(
            text=f"bot開発者: {str(tari3210)}", icon_url=tari3210.display_avatar.url)
        JST = datetime.timezone(datetime.timedelta(hours=9))
        embed.timestamp = datetime.datetime.now(JST)
        await message.channel.send(embed=embed)
        embed.title = "対戦カード"
        await pairing_channel.send(vc_role.mention, embed=embed)
        await pairing_channel.send(f"{bs_role.mention}\n\n{bbx_mic.mention} を確認して、マイク設定を行ってからの参加をお願いします。\n\n※スマホユーザーの方へ\nspeakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります")
        await chat.send(embeds=[embed, embed_chat_info])
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="BATTLE STADIUM")
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
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
            if scheduled_event.status == discord.ScheduledEventStatus.active and scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.complete()
        try:
            instance = await stage.fetch_instance()
        except discord.errors.NotFound:
            pass
        else:
            await instance.delete()
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        return

    if message.content.startswith("s.bs"):
        await message.delete(delay=1)
        JST = datetime.timezone(datetime.timedelta(hours=9))
        dt_now = datetime.datetime.now(JST)
        sat = datetime.timedelta(days=6 - int(dt_now.strftime("%w")))
        start_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 21, 30, 0, 0, JST) + sat
        end_time = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day, 22, 30, 0, 0, JST) + sat
        stage = client.get_channel(931462636019802123)  # BATTLE STADIUM
        event = await message.guild.create_scheduled_event(name="BATTLE STADIUM", description="今週もやります！\nこのイベントの趣旨は「とにかくBeatboxバトルをすること」です。いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。", start_time=start_time, end_time=end_time, location=stage)
        embed = Embed(title="BATTLE STADIUM 開催のお知らせ", description="```今週もやります！\nこのイベントの趣旨は「とにかくBeatboxバトルをすること」です。いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。```", color=0x00bfff)
        embed.add_field(name="日時 date", value=start_time.strftime(
            '%m/%d 21:30 - 22:30 Japan time'), inline=False)
        embed.add_field(name="場所 place",
                        value=f'stage channel {stage.mention}', inline=False)
        await message.channel.send(embed=embed)
        await message.channel.send(event.url)
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
