import discord
client = discord.Client()
print("successfully started")
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "!join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してください。")
            return
        await message.author.voice.channel.connect()
        await message.channel.send("接続しました。")
    
    if message.content == "!leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
    
    if message.content == "!play time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("time.mp3"))  
        return
          
    if message.content == "!play kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("kansei.mp3"))  
        return

    if message.content == "!play countdown":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
        message.guild.voice_client.play(discord.FFmpegPCMAudio("countdown.mp3"))  
        return

    if message.context =="!help":
        await message.channel.send("コマンド一覧")
        await message.channel.send("`!join コマンドを打った人が居るVCチャンネルに接続`")
        await message.channel.send("`!leave VCチャンネルから切断`")
        await message.channel.send("`!play countdown 321beatboxの音声`")
        await message.channel.send("`!play time timeの音声`")
        await message.channel.send("`!play kansei` 歓声")

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")