import discord
import random
from time import sleep
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
            sleep(4)
            i = 0
            if timer_int > 10:
                for i in range(timer_int):
                    sleep(1)
            else:
                counter = 10
                for i in range(timer_int * 5):
                    sleep(10)
                    await message.channel.send(str(counter) + "秒経過")
                    counter += 10
                sleep(10)
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
        sleep(3)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        sleep(5)
        await message.guild.voice_client.disconnect()
        await message.channel.send("ss.join")
        return

    if message.content == "s.c2":
        await message.channel.send("タイマースタート!")
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("s.battle"):
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            return
        await message.channel.send("1minute 2round\n5秒後にスタートします。\n\nAre you ready??")
        sleep(5)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.5)
        await message.channel.send("3, 2, 1, Beatbox!")
        message.guild.voice_client.play(audio)
        sleep(3)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", description="Round1", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", description="Round1", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round1", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round2switch.mp3"), volume=0.5)
        await message.channel.send("----------\n\nTIME!\nRound2 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        sleep(3)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", description="Round2", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", description="Round2", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round2", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round3switch.mp3"), volume=0.5)
        await message.channel.send("----------\n\nTIME!\nRound3 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        sleep(3)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", description="Round3", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", description="Round3", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round3", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round4switch.mp3"), volume=0.5)
        await message.channel.send("----------\n\nTIME!\nRound4 SWITCH!\n\n----------")
        message.guild.voice_client.play(audio)
        sleep(3)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り40秒", description="Round4", color=0x00ff00)
        await message.channel.send(embed=embed)
        sleep(10)
        sleep(10)
        embed = discord.Embed(title="残り20秒", description="Round4", color=0xffff00)
        await message.channel.send(embed=embed)
        sleep(10)
        embed = discord.Embed(title="残り10秒", description="Round4", color=0xff0000)
        await message.channel.send(embed=embed)
        sleep(10)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
        embed = discord.Embed(title="TIME!")
        await message.channel.send(embed=embed)
        message.guild.voice_client.play(audio)
        return

    if len(message.content) > 10:
        a = random.randint(1, 200)
        sleep(2)
        if a == 1:
            await message.channel.send("ｵﾝｷﾞｬｱｱｱｱｱｱｱｱｱｱｱｱｱ！！！！！")
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
