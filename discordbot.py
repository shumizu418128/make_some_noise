import discord
import random
from asyncio import sleep
intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = discord.Client(intents=intents)
print("successfully started")

@client.event
async def on_message(message):
    if message.content == "s.join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except discord.errors.ClientException:
            await message.channel.send("既に接続しています。\nチャンネルを移動させたい場合、一度切断してからもう一度お試しください。")
        else:
            await message.channel.send("接続しました。")
            return

    if message.content == "s.leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
        return

    if message.content == "s.p time" or message.content == "s.time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "time.mp3", 2: "time_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.3)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3", 3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.t"):
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
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
            await sleep(4)
            i = 0
            if timer_int > 10:
                for i in range(timer_int):
                    await sleep(1)
            else:
                counter = 10
                for i in range(timer_int * 5):
                    await sleep(10)
                    await message.channel.send(str(counter) + "秒経過")
                    counter += 10
                await sleep(10)
            embed = discord.Embed(title="TIME!")
            await message.channel.send(embed=embed)
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            return

    if message.content == "s.help":
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.t` タイマーを利用できます。詳細はs.help timeと入力すると確認できます。\n`s.p count or s.count` 321beatboxの音声\n`s.p time or s.time` timeの音声\n`s.p kbbtime or s.kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei or s.kansei` 歓声\n`s.p bunka or s.bunka` 文化の人の音声\n`s.p esh or s.esh` eshの音声\n`s.p msn or s.msn` make some noiseの音声\n`s.p olala or s.olala` olalaの音声")
        await message.channel.send("make some noise bot開発者：tari3210 #9924")
        return

    if message.content == "s.help time":
        await message.channel.send("タイマー利用方法\n\n`s.t`の後ろに、半角スペースを空けて数字を入力してください。\n例：`s.t 3` \n1から10まで数字は分単位で、それ以上の数字は秒単位でセットされます。\n例1：1分40秒にセットしたい場合 `s.t 100`\n例2：3分にセットしたい場合 `s.t 3`もしくは`s.t 180`\n\n注意：必ず整数で入力してください。")
        return

    if message.content == "s.c":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        await message.channel.send("3, 2, 1, Beatbox!")
        message.guild.voice_client.play(audio)
        await sleep(23)
        embed = discord.Embed(title="残り40秒", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        await sleep(5)
        await message.guild.voice_client.disconnect()
        await message.channel.send("ss.join")
        return

    if message.content == "s.c2":
        await message.channel.send("タイマースタート!")
        await sleep(20)
        embed = discord.Embed(title="残り40秒", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("s.order"):
        names = [(j) for j in message.content.split()]
        names.remove("s.order")
        random.shuffle(names)
        count, count2 = 0, 1
        await message.channel.send("処理に時間がかかります。\n「処理終了」と表示されるまで **何も書き込まず** お待ちください。\n対戦カード：")
        while count < len(names):
            await message.channel.send("第" + str(count2) + "試合：" + names[count] + " VS " + names[count + 1])
            count += 2
            count2 += 1
        list = []
        for i in names:
            list.append(i)
        list = ', '.join(list)
        await message.channel.send("トーナメント表書き込み順（上から）：\n" + list + "\n\n――――――処理終了――――――")
        return

    if message.content.startswith("s.battle"):
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        names = [(j) for j in message.content.split()]
        if len(names) < 3:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        await message.channel.send(names[1] + "さん(1st) vs " + names[2] + "さん(2nd)\n\n1分・2ラウンドずつ\n1 minute, 2 rounds each\n\n5秒後にスタートします。\nAre you ready??")
        await sleep(5)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        await message.channel.send("3, 2, 1, Beatbox!")
        message.guild.voice_client.play(audio)
        await sleep(23)
        embed = discord.Embed(title="残り40秒", description="Round1", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", description="Round1", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round1", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round2switch.mp3"), volume=1)
        await message.channel.send("----------\n\nTIME!\nRound2 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        await sleep(23)
        embed = discord.Embed(title="残り40秒", description="Round2", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", description="Round2", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round2", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round3switch.mp3"), volume=1)
        await message.channel.send("----------\n\nTIME!\nRound3 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        await sleep(23)
        embed = discord.Embed(title="残り40秒", description="Round3", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", description="Round3", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round3", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round4switch.mp3"), volume=1)
        await message.channel.send("----------\n\nTIME!\nRound4 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        await sleep(23)
        embed = discord.Embed(title="残り40秒", description="Round4", color=0x00ff00)
        await message.channel.send(embed=embed)
        await sleep(20)
        embed = discord.Embed(title="残り20秒", description="Round4", color=0xffff00)
        await message.channel.send(embed=embed)
        await sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round4", color=0xff0000)
        await message.channel.send(embed=embed)
        await sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        message.guild.voice_client.play(audio)
        return

    if message.content.startswith("s.role"):
        input_id = [(j) for j in message.content.split()]
        try:
            role = message.guild.get_role(int(input_id[1]))
        except ValueError:
            await message.channel.send("Error: type ID")
            return
        else:
            try:
                role_member = role.members
            except AttributeError:
                await message.channel.send("Error: Role not found")
                return
            else:
                for member in role_member:
                    await message.channel.send(member.display_name)
                await message.channel.send("---finish---")
                return

    if message.content == "s.start":
        role = message.guild.get_role(930368130906218526)  # test role
        role_member = role.members
        await message.channel.send("処理中...")
        for member in role_member:
            print(member.display_name + " をロールから削除")
            await member.remove_roles(role)
        channel = client.get_channel(930446820839157820)  # test category エントリー
        message2 = await channel.fetch_message(930448529787351130)  # carl-botのメッセージ エントリー開始用
        await message2.clear_reaction("✅")
        await message2.add_reaction("✅")
        await message.channel.send("処理完了")
        embed = discord.Embed(title="受付開始", description="ただいまより参加受付を開始します。\n専用テキストチャンネルにてエントリーを行ってください。\n\n1分後に締め切ります。", color=0x00bfff)
        await message.channel.send(embed=embed)
        for i in range(3):
            await sleep(10)
        await message.channel.send("あと30秒で締め切ります。")
        print("あと30秒で締め切ります。")
        await sleep(20)
        await message.channel.send("締め切り10秒前")
        print("締め切り10秒前")
        await sleep(10)
        await message2.clear_reaction("✅")
        await message.channel.send("参加受付を締め切りました。\n\n処理中... しばらくお待ちください")
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
        embed = discord.Embed(title="抽選結果", color=0xff9900)
        while counter2 + 2 <= len(playerlist):
            embed.add_field(name="Match%s" % (str(counter)), value="%s vs %s" % (playerlist[counter2], playerlist[counter2 + 1]), inline=False)
            counter += 1
            counter2 += 2
        if len(playerlist) % 2 == 1:
            await message.channel.send("参加人数が奇数でした。\n" + playerlist[0] + " さんの対戦が2回行われます。")
            embed.add_field(name="Match%s" % (str(counter)), value="%s vs %s" % (playerlist[0], playerlist[-1]), inline=False)
        await message.channel.send(embed=embed)
        channel2 = client.get_channel(930767329137143839)
        await channel2.send(embed=embed)
        if message.guild.voice_client is not None:
            await message.guild.voice_client.disconnect()
        voice_channel = client.get_channel(930446857660928031)
        await voice_channel.connect(reconnect=True)
        return

    if len(message.content) > 10:
        a = random.randint(1, 200)
        await sleep(2)
        if a == 1:
            await message.channel.send("ｵﾝｷﾞｬｱｱｱｱｱｱｱｱｱｱｱｱｱ！！！！！")
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
