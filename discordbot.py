import discord
import random
from time import sleep
client = discord.Client()
print("successfully started")
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "s.join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        await message.author.voice.channel.connect()
        await message.channel.send("接続しました。")

    if message.content == "s.leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")

    if message.content == "s.p time" or message.content == "s.time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        ran_int = random.randint(1, 2)
        ran_audio = {1: "time.mp3", 2: "time_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p count" or message.content == "s.count":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.1)
        message.guild.voice_client.play(audio)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.3)
        message.guild.voice_client.play(audio)
        return

    if "s.t" in message.content:
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
        timer = message.content.split(" ")
        try:
            timer_int = int(timer[1])
        except BaseException:
            await message.channel.send("入力方法が間違っています。正しい入力方法は、s.help timeと入力すると確認できます。")
        else:
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.1)
            message.guild.voice_client.play(audio)
            sleep(4)
            if timer_int > 10:
                sleep(timer_int)
            else:
                sleep(timer_int * 60)
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.1)
            message.guild.voice_client.play(audio)
        return

    if "め" in message.content:
        a = random.randint(1, 10000)
        sleep(2)
        if a == 1:
            await message.channel.send("ｵﾝｷﾞｬｱｱｱｱｱｱｱｱｱｱｱｱｱ！！！！！")
        return

    if message.content == "s.help":
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.t` タイマーを利用できます。詳細はs.help timeと入力すると確認できます。\n`s.p count or s.count` 321beatboxの音声\n`s.p time or s.time` timeの音声\n`s.p kbbtime or s.kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei or s.kansei` 歓声\n`s.p bunka or s.bunka` 文化の人の音声\n`s.p esh or s.esh` eshの音声\n`s.p msn or s.msn` make some noiseの音声")
        await message.channel.send("bot開発者：tari3210 #9924\nコマンド追加要望やバグ等ありましたら、いつでもご連絡ください。")
        return

    if message.content == "s.help time":
        await message.channel.send("タイマー利用方法\n\n`s.t`の後ろに、半角スペースを空けて数字を入力してください。\n例：`s.t 3` \n1から10まで数字は分単位で、それ以上の数字は秒単位でセットされます。\n例1：1分40秒にセットしたい場合 `s.t 100`\n例2：3分にセットしたい場合 `s.t 3`もしくは`s.t 180`\n\n注意：必ず整数で入力してください。")
        return

    if message.content == "s.c":
        await message.channel.send("3, 2, 1, Beatbox!")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.1)
        message.guild.voice_client.play(audio)
        sleep(33)
        await message.channel.send("残り30秒")
        sleep(10)
        sleep(10)
        await message.channel.send("残り10秒")
        sleep(7)
        await message.channel.send("3")
        sleep(1)
        await message.channel.send("2")
        sleep(1)
        await message.channel.send("1")
        sleep(1)
        await message.channel.send("TIME!")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.1)
        message.guild.voice_client.play(audio)
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
