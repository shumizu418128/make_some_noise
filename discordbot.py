import discord
client = discord.Client()
print("successfully started")
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "s.join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してください。")
            return
        await message.author.voice.channel.connect()
        await message.channel.send("接続しました。")
    
    if message.content == "s.leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
    
    if message.content == "s.play time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("time.mp3"))  
        return
          
    if message.content == "s.play kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("kansei.mp3"))  
        return

    if message.content == "s.play countdown":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("countdown.mp3"))  
        return

    if message.content =="s.help":
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.play countdown` 321beatboxの音声\n`s.play time` timeの音声\n`s.play kansei` 歓声")

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
