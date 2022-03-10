import discord
import random
import datetime
from asyncio import sleep
import asyncio
intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = discord.Client(intents=intents)
print("successfully started")

@client.event
async def on_voice_state_update(member, before, after):
    role = member.guild.get_role(935073171462307881)  # in a vc
    if before.channel is None and after.channel is not None:
        await member.add_roles(role)
        return
    if before.channel is not None and after.channel is None:
        await member.remove_roles(role)
        return

@client.event
async def on_member_update(before, after):
    if str(before.roles) != str(after.roles):
        check_role_before = before.roles
        check_role_after = after.roles
        id_list_before = []
        id_list_after = []
        for id in check_role_before:
            id_list_before.append(id.id)
        for id in check_role_after:
            id_list_after.append(id.id)
        channel = client.get_channel(916608669221806100)  # ビト森杯 進行bot
        channel2 = client.get_channel(930447365536612353)  # bot - battle stadium
        if 930368130906218526 in id_list_after and 930368130906218526 not in id_list_before:  # battle stadium
            notice = await channel2.send(f"{after.mention}\nエントリーを受け付けました\nentry completed👍")
            await notice.delete(delay=5)
        if 920320926887862323 in id_list_after and 920320926887862323 not in id_list_before:  # A部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🇦部門\nエントリーを受け付けました：{after.display_name}さん\nentry completed👍\n\n名前を変更する際は、一度エントリーをキャンセルしてください。")
        if 920320926887862323 in id_list_before and 920320926887862323 not in id_list_after:  # A部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🇦部門\nエントリーを取り消しました❎\nentry canceled")
        if 920321241976541204 in id_list_after and 920321241976541204 not in id_list_before:  # B部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🅱️部門\nエントリーを受け付けました：{after.display_name}さん\nentry completed👍\n\n名前を変更する際は、一度エントリーをキャンセルしてください。")
        if 920321241976541204 in id_list_before and 920321241976541204 not in id_list_after:  # B部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🅱️部門\nエントリーを取り消しました❎\nentry canceled")
        return

@client.event
async def on_message(message):
    if message.channel.id == 930767329137143839:  # バトスタ対戦表
        if message.author.bot:
            return
        await message.delete(delay=1)
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
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3", 3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.t"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        timer = message.content.split(" ")
        try:
            timer_int = int(timer[1])
        except BaseException:
            await message.channel.send("入力方法が間違っています。正しい入力方法は、s.help timeと入力すると確認できます。")
            return
        else:
            await message.channel.send("3, 2, 1, Beatbox!")
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            await sleep(7)
            i = 0
            if timer_int > 10:
                for i in range(timer_int):
                    await sleep(1)
                    if i % 10 == 9:
                        notice = await message.channel.send(str(i + 1) + "秒経過")
                        await notice.delete(delay=20)
            else:
                counter = 10
                for i in range(timer_int * 6):
                    await sleep(10)
                    notice = await message.channel.send(str(counter) + "秒経過")
                    await notice.delete(delay=20)
                    counter += 10
            embed = discord.Embed(title="TIME!")
            await message.channel.send(embed=embed)
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            return

    if message.content == "s.help":
        await message.delete(delay=1)
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.t` タイマーを利用できます。詳細はs.help timeと入力すると確認できます。\n`s.p count or s.count` 321beatboxの音声\n`s.p time or s.time` timeの音声\n`s.p kbbtime or s.kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei or s.kansei` 歓声\n`s.p bunka or s.bunka` 文化の人の音声\n`s.p esh or s.esh` eshの音声\n`s.p msn or s.msn` make some noiseの音声\n`s.p olala or s.olala` olalaの音声")
        await message.channel.send("make some noise bot開発者：tari3210 #9924")
        return

    if message.content == "s.help time":
        await message.delete(delay=1)
        await message.channel.send("タイマー利用方法\n\n`s.t`の後ろに、半角スペースを空けて数字を入力してください。\n例：`s.t 3` \n1から10まで数字は分単位で、それ以上の数字は秒単位でセットされます。\n例1：1分40秒にセットしたい場合 `s.t 100`\n例2：3分にセットしたい場合 `s.t 3`もしくは`s.t 180`\n\n注意：必ず整数で入力してください。")
        return

    if message.content.startswith("s.c"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [(j) for j in message.content.split()]
        names.remove("s.c")
        if len(names) == 0:
            await message.delete(delay=1)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            start = await message.channel.send("3, 2, 1, Beatbox!")
            await start.delete(delay=10)
            message.guild.voice_client.play(audio)
            await sleep(7)
            embed = discord.Embed(title="1:00", color=0x00ff00)
            sent_message = await message.channel.send(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = discord.Embed(title=f"{counter}", color=color)
                await sent_message.edit(embed=embed)
                counter -= 10
                if i == 1:
                    color = 0xffff00
                elif i == 3:
                    color = 0xff0000
            await sleep(9.9)
            embed = discord.Embed(title="TIME!")
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)

        elif len(names) == 2 or len(names) == 3:
            round_count = 1
            if len(names) == 3:
                round_count = int(names[2])
                embed = discord.Embed(title="再開コマンド", description=f"Round{names[2]}から再開します")
                await message.channel.send(embed=embed)
                del names[2]
                if round_count % 2 == 0:
                    names.reverse()
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
            start = await message.channel.send("3, 2, 1, Beatbox!")
            await start.delete(delay=10)
            message.guild.voice_client.play(audio)
            await sleep(7)
            embed = discord.Embed(title="1:00", description=f"Round{round_count} {names[0]}", color=0x00ff00)
            sent_message = await message.channel.send(embed=embed)
            while round_count < 5:
                timeout = 10
                counter = 50
                color = 0x00ff00
                for i in range(7):
                    def check(reaction, user):
                        id_manage = 904368977092964352  # ビト森杯運営
                        roles = user.roles
                        id_list = [role.id for role in roles]
                        return id_manage in id_list and str(reaction.emoji) == '⏭️'
                    try:
                        await client.wait_for('reaction_add', timeout=timeout, check=check)
                    except asyncio.TimeoutError:
                        if counter == -10:
                            await message.channel.send("Error: timeout\nタイマーを停止しました")
                            return
                        embed = discord.Embed(title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
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
                                embed = discord.Embed(title="0", description=f"Round4 {names[0]}", color=color)
                                await sent_message.edit(embed=embed)
                                break
                        continue
                    else:
                        break
                embed = discord.Embed(title="TIME!")
                await sent_message.edit(embed=embed)
                await sent_message.delete(delay=5)
                names.reverse()
                round_count += 1
                if round_count < 5:
                    switch = await message.channel.send("SWITCH!")
                    await switch.delete(delay=5)
                    embed = discord.Embed(title="1:00", description=f"Round{round_count} {names[0]}", color=0x00ff00)
                    sent_message = await message.channel.send(embed=embed)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            await sleep(3)
            audio = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
            message.guild.voice_client.play(audio)
            await message.delete(delay=1)
        else:
            await message.channel.send("Error: 入力方法が間違っています。")
        return

    if message.content.startswith("s.bj"):
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        names = [(j) for j in message.content.split()]
        names.remove("s.bj")
        round_count = 1
        if len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        start = await message.channel.send("3, 2, 1, Beatbox!")
        await start.delete(delay=10)
        message.guild.voice_client.play(audio)
        await sleep(7)
        embed = discord.Embed(title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        while round_count < 5:
            timeout = 10
            counter = 80
            color = 0x00ff00
            while True:
                def check(reaction, user):
                    return user.bot is False and str(reaction.emoji) == '⏭️'
                try:
                    await client.wait_for('reaction_add', timeout=timeout, check=check)
                except asyncio.TimeoutError:
                    if counter == -10:
                        await message.channel.send("Error: timeout\nタイマーを停止しました")
                        return
                    embed = discord.Embed(title=f"{counter}", description=f"Round{round_count} {names[0]}", color=color)
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
                            embed = discord.Embed(title="0", description=f"Round4 {names[0]}", color=color)
                            await sent_message.edit(embed=embed)
                            break
                    continue
                else:
                    break
            embed = discord.Embed(title="TIME!")
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            names.reverse()
            round_count += 1
            if round_count < 5:
                switch = await message.channel.send("SWITCH!")
                await switch.delete(delay=5)
                embed = discord.Embed(title="90", description=f"Round{round_count} {names[0]}", color=0x00ff00)
                sent_message = await message.channel.send(embed=embed)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await sleep(3)
        audio = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)

    if message.content == "s.c90":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
        embed = discord.Embed(title="90", color=0x00ff00)
        sent_message = await message.channel.send(embed=embed)
        counter = 80
        color = 0x00ff00
        for i in range(8):
            await sleep(9.9)
            embed = discord.Embed(title=f"{counter}", color=color)
            await sent_message.edit(embed=embed)
            counter -= 10
            if i == 4:
                color = 0xffff00
            elif i == 6:
                color = 0xff0000
        await sleep(9.9)
        embed = discord.Embed(title="TIME!")
        await sent_message.edit(embed=embed)
        await sent_message.delete(delay=5)
        return

    if message.content.startswith("s.battle"):
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        VoiceClient = message.guild.voice_client
        me = message.guild.get_member(896652783346917396)  # make some noise!
        try:
            await me.edit(suppress=False)
        except AttributeError:
            pass
        names = [(j) for j in message.content.split()]
        count = 1
        if len(names) == 4:
            try:
                count = int(names[3])
            except ValueError:
                await message.channel.send("Error: 入力方法が間違っています。")
                return
            if count > 4 or count == 1:
                await message.channel.send("Error: 入力方法が間違っています。")
                return
            embed = discord.Embed(title="再開コマンド", description="Round%sから再開します。\n\n※意図していない場合、`s.leave`と入力してbotを停止した後、再度入力してください。" % (str(count)))
            await message.channel.send(embed=embed)
            del names[3]
        elif len(names) != 3:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        names.remove("s.battle")
        await message.channel.send(names[0] + "さん `1st` vs " + names[1] + "さん `2nd`\n\n1分・2ラウンドずつ\n1 minute, 2 rounds each\n\nAre you ready??")
        if count % 2 == 0:
            names.reverse()
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("battle_start.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        await sleep(11)
        connect = VoiceClient.is_connected()
        if connect is False:
            await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
            return
        await message.channel.send("3, 2, 1, Beatbox!")
        await sleep(3)
        while count <= 4:
            embed = discord.Embed(title="1:00", description="Round%s %s" % (str(count), names[0]), color=0x00ff00)
            sent_message = await message.channel.send(embed=embed)
            counter = 50
            color = 0x00ff00
            for i in range(5):
                await sleep(9.9)
                embed = discord.Embed(title=f"{counter}", description="Round%s %s" % (str(count), names[0]), color=color)
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
            await sleep(9.9)
            embed = discord.Embed(title=f"{counter}", description="Round%s %s" % (str(count), names[0]))
            await sent_message.edit(embed=embed)
            await sent_message.delete(delay=5)
            if count <= 3:
                audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round%sswitch.mp3" % (str(count + 1))), volume=1.5)
                connect = VoiceClient.is_connected()
                if connect is False:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                message.guild.voice_client.play(audio)
                switch = await message.channel.send("--------------------\n\nTIME!\nRound%s %s\nSWITCH!\n\n--------------------" % (str(count + 1), names[1]))
                await switch.delete(delay=5)
                names.reverse()
                await sleep(3)
            count += 1
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        random_fuga = random.randint(1, 10)
        if random_fuga == 1:
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time_3.mp3"), volume=0.3)
            message.guild.voice_client.play(audio)
            await sleep(8)
            message4 = await message.channel.send("なああああああああああああああああああああああああああああああああああ")
            await message4.add_reaction("🗿")
            return
        message.guild.voice_client.play(audio)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        embed = discord.Embed(title="投票箱", description="`1st:`%s\n`2nd:`%s\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。" % (names[1], names[0]))
        role_vc = message.guild.get_role(935073171462307881)  # in a vc
        message3 = await message.channel.send(content=role_vc.mention, embed=embed)
        await message3.add_reaction("1⃣")
        await message3.add_reaction("2⃣")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        await sleep(3)
        message.guild.voice_client.play(audio)
        message4 = await message.channel.send("make some noise for the battle!\ncome on!!")
        await message4.add_reaction("🔥")
        return

    if message.content.startswith("s.role"):
        await message.delete(delay=1)
        input_id = [(j) for j in message.content.split()]
        try:
            role = message.guild.get_role(int(input_id[1]))
        except ValueError:
            await message.channel.send("Error: ロールIDを入力してください")
            return
        else:
            try:
                role_member = role.members
            except AttributeError:
                await message.channel.send("Error: ロールが見つかりませんでした")
                return
            else:
                for member in role_member:
                    await message.channel.send(member.display_name, member.id)
                await message.channel.send("---finish---")
                return

    if message.content == "s.start":
        await message.channel.send("処理中...")
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        scheduled_events = message.guild.scheduled_events
        if len(scheduled_events) == 1:
            try:
                await scheduled_events[0].start()
            except discord.errors.HTTPException:
                pass
        else:
            try:
                await stage_channel.create_instance(topic="battle stadium")
            except discord.errors.HTTPException:
                pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        me = message.guild.get_member(896652783346917396)  # make some noise!
        await me.edit(suppress=False)
        channel0 = client.get_channel(930767329137143839)  # 対戦表
        await channel0.purge()
        role = message.guild.get_role(930368130906218526)  # battle stadium
        role_member = role.members
        for member in role_member:
            await member.remove_roles(role)
        channel1 = client.get_channel(930446820839157820)  # 参加
        message2 = await channel1.fetch_message(931879656213319720)  # carl-botのメッセージ エントリー開始用
        await message2.clear_reaction("✅")
        await message2.add_reaction("✅")
        await message.channel.send("処理完了")
        embed = discord.Embed(title="受付開始", description="ただいまより参加受付を開始します。\n%sにてエントリーを行ってください。\nentry now accepting at %s" % (channel1.mention, channel1.mention), color=0x00bfff)
        await message.channel.send(embed=embed)
        role_vc = message.guild.get_role(935073171462307881)  # in a vc
        bbx_mic = client.get_channel(931781522808262756)  # bbxマイク設定
        notice = await channel1.send("%s\nエントリー後に、 %s を確認して、マイク設定を行ってください。" % (role_vc.mention, bbx_mic.mention))
        await notice.delete(delay=60)
        await sleep(30)
        embed = discord.Embed(title="あと30秒で締め切ります", color=0xffff00)
        await message.channel.send(embed=embed)
        await message.channel.send(role_vc.mention)
        await sleep(20)
        embed = discord.Embed(title="締め切り10秒前", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        await message2.clear_reaction("✅")
        await message.channel.send("参加受付を締め切りました。\nentry closed\n\n処理中... しばらくお待ちください")
        role_member = role.members
        playerlist = []
        for member in role_member:
            playerlist.append(member.display_name)
        random.shuffle(playerlist)
        if len(playerlist) < 2:
            embed = discord.Embed(title="Error", description="参加者が不足しています。", color=0xff0000)
            await message.channel.send(embed=embed)
            return
        counter = 1
        counter2 = 0
        dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        date = str(dt_now.strftime('%m月%d日 %H:%M')) + " JST"
        if date[3] == "0":
            date = date[:2] + date[4:]
        if date[0] == "0":
            date = date[1:]
        embed = discord.Embed(title="抽選結果", description="%s" % (date), color=0xff9900)
        while counter2 + 2 <= len(playerlist):
            embed.add_field(name="Match%s" % (str(counter)), value="%s `1st` vs %s `2nd`" % (playerlist[counter2], playerlist[counter2 + 1]), inline=False)
            counter += 1
            counter2 += 2
        if len(playerlist) % 2 == 1:
            await message.channel.send("----------------------------------------\n\n参加人数が奇数でした。\n" + playerlist[0] + " さんの対戦が2回行われます。")
            await channel0.send("参加人数が奇数でした。\n" + playerlist[0] + " さんの対戦が2回行われます。")
            embed.add_field(name="Match%s" % (str(counter)), value="%s `1st` vs %s `2nd`" % (playerlist[-1], playerlist[0]), inline=False)
        await message.channel.send(embed=embed)
        embed.title = "対戦カード"
        await channel0.send(embed=embed)
        await channel0.send("%s\n\n%s を確認して、マイク設定を行ってからの参加をお願いします。\n\n※スマホユーザーの方へ\nspeakerになった後、ミュート以外画面操作を一切行わないでください\nDiscordバグにより音声が一切入らなくなります" % (role.mention, bbx_mic.mention))
        return

    if message.content == "s.stage":
        await message.delete(delay=1)
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="battle stadium")
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        me = message.guild.get_member(896652783346917396)  # make some noise!
        await me.edit(suppress=False)
        return

    if message.content.startswith("s.entry"):
        input_ = message.content[8:]  # s.entry をカット
        try:
            name = message.guild.get_member(int(input_))
        except ValueError:
            name = message.guild.get_member_named(input_)
        if name is None:
            await message.channel.send("検索結果なし")
            return
        roles = name.roles
        for role in roles:
            if role.id == 920320926887862323:  # A部門 ビト森杯
                await message.channel.send("%sさんはビト森杯 🇦部門エントリー済み" % (name.display_name))
                return
            if role.id == 920321241976541204:  # B部門 ビト森杯
                await message.channel.send("%sさんはビト森杯 🅱️部門エントリー済み" % (name.display_name))
                return
        await message.channel.send("%sさんはビト森杯にエントリーしていません" % (name.display_name))
        return

    if message.content == "s.end":
        await message.delete(delay=1)
        scheduled_events = message.guild.scheduled_events
        if len(scheduled_events) == 1:
            await scheduled_events[0].complete()
        channel0 = client.get_channel(930767329137143839)  # 対戦表
        await channel0.purge()
        role = message.guild.get_role(930368130906218526)  # battle stadium
        role_member = role.members
        for member in role_member:
            await member.remove_roles(role)
        stage = client.get_channel(931462636019802123)  # ステージ
        chat = client.get_channel(864475338340171795)  # 雑談部屋1
        members = stage.members
        for member in members:
            await member.move_to(chat)
        return

    if message.content.startswith("s.poll"):
        names = [(j) for j in message.content.split()]
        names.remove("s.poll")
        if len(names) != 2:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        embed = discord.Embed(title="投票箱", description="1⃣ %s\n2⃣ %s" % (names[0], names[1]))
        poll = await message.channel.send(embed=embed)
        await poll.add_reaction("1⃣")
        await poll.add_reaction("2⃣")
        return

    if message.content.startswith("s.cancel"):
        input_ = message.content[9:]  # s.cancel をカット
        try:
            name = message.guild.get_member(int(input_))
        except ValueError:
            name = message.guild.get_member_named(input_)
        if name is None:
            await message.channel.send("検索結果なし")
            return
        roles = name.roles
        for role in roles:
            if role.id == 920320926887862323:  # A部門 ビト森杯
                roleA = message.guild.get_role(920320926887862323)  # A部門 ビト森杯
                await name.remove_roles(roleA)
                await message.channel.send("%sさんのビト森杯 🇦部門エントリーを取り消しました。" % (name.display_name))
                return
            if role.id == 920321241976541204:  # B部門 ビト森杯
                roleB = message.guild.get_role(920321241976541204)  # B部門 ビト森杯
                await name.remove_roles(roleB)
                await message.channel.send("%sさんのビト森杯 🅱️部門エントリーを取り消しました。" % (name.display_name))
                return
        await message.channel.send("%sさんはビト森杯にエントリーしていません" % (name.display_name))
        return

    if "s." not in message.content:
        if message.author.bot:
            return
        elif message.channel.id == 930447365536612353:
            await message.delete(delay=1)
        else:
            a = random.randint(1, 400)
            await sleep(2)
            if a == 1:
                await message.channel.send("ｵﾝｷﾞｬｱｱｱｱｱｱｱｱｱｱｱｱｱ！！！！！")
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
