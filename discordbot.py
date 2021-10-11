import discord
client = discord.Client()
print("successfully started")
@client.event


async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "s.join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう１度お試しください。")
            return
        await message.author.voice.channel.connect()
        await message.channel.send("接続しました。")
    
    if message.content == "s.leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
    
    if message.content == "s.p time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう１度お試しください。")
        time = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.1)
        message.guild.voice_client.play(time)  
        return
    
    if message.content == "s.p kbbtime":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう１度お試しください。")
        kbbtime = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.1)
        message.guild.voice_client.play(kbbtime)  
        return
          
    if message.content == "s.p kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう１度お試しください。")
        kansei = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kansei.mp3"), volume=0.1)
        message.guild.voice_client.play(kansei)  
        return

    if message.content == "s.p count":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう１度お試しください。")
        count = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("countdown.mp3"), volume=0.1)
        message.guild.voice_client.play(count)  
        return
    
    if message.content == "s.p bunka":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう１度お試しください。")
        bunka = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.1)
        message.guild.voice_client.play(bunka)  
        return

    if message.content =="s.help":
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.p count` 321beatboxの音声\n`s.p time` timeの音声\n`s.p kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei` 歓声\n`s.p bunka` 文化の人の音声")
        await message.channel.send("bot開発者：tari3210 #9924\nコマンド追加要望やバグ等ありましたら、いつでもご連絡ください。")
client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
