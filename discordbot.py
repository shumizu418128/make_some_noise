import discord
import random
import datetime
from asyncio import sleep
intents = discord.Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = discord.Client(intents=intents)
print("successfully started")

@client.event
async def on_voice_state_update(member, before, after):
    guild = client.get_guild(864475338340171786)  # サーバーID
    role = guild.get_role(935073171462307881)  # in a vc
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
        channel = client.get_channel(864475338340171791)  # 全体チャット
        if 930368130906218526 in id_list_after and 930368130906218526 not in id_list_before:  # battle stadium
            notice = await channel.send(f"{after.mention}\nエントリーを受け付けました\nentry completed👌")
            await notice.delete(delay=5)
        if 920320926887862323 in id_list_after and 920320926887862323 not in id_list_before:  # A部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🇦部門\nエントリーを受け付けました👌\nentry completed")
        if 920320926887862323 in id_list_before and 920320926887862323 not in id_list_after:  # A部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🇦部門\nエントリーを取り消しました❎\nentry canceled")
        if 920321241976541204 in id_list_after and 920321241976541204 not in id_list_before:  # B部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🅱️部門\nエントリーを受け付けました👌\nentry completed")
        if 920321241976541204 in id_list_before and 920321241976541204 not in id_list_after:  # B部門ビト森杯
            await channel.send(f"{after.mention}\nビト森杯🅱️部門\nエントリーを取り消しました❎\nentry canceled")
        return

@client.event
async def on_message(message):
    if message.channel.id == 930767329137143839:
        if message.author.bot:
            return
        await message.delete(delay=1)
        return

    if message.content == "s.join":
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except discord.errors.ClientException:
            await message.channel.send("既に接続しています。\nチャンネルを移動させたい場合、一度切断してからもう一度お試しください。")
            await message.delete(delay=1)
            return
        else:
            await message.channel.send("接続しました。")
            await message.delete(delay=1)
            return

    if message.content == "s.leave":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            await message.delete(delay=1)
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
        await message.delete(delay=1)
        return

    if message.content == "s.p time" or message.content == "s.time":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "time.mp3", 2: "time_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p kbbtime" or message.content == "s.kbbtime":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("kbbtime.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p kansei" or message.content == "s.kansei":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "kansei.mp3", 2: "kansei_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.3)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p count" or message.content == "s.count":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "countdown.mp3", 2: "countdown_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.2)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p bunka" or message.content == "s.bunka":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0.2)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p esh" or message.content == "s.esh":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        ran_int = random.randint(1, 2)
        ran_audio = {1: "esh.mp3", 2: "esh_2.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=0.4)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p msn" or message.content == "s.msn":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p olala" or message.content == "s.olala":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("olala.mp3"), volume=0.4)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content == "s.p dismuch" or message.content == "s.dismuch":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
            return
        ran_int = random.randint(1, 4)
        ran_audio = {1: "dismuch.mp3", 2: "dismuch_2.mp3", 3: "dismuch_3.mp3", 4: "dismuch_4.mp3"}
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ran_audio[ran_int]), volume=1)
        message.guild.voice_client.play(audio)
        await message.delete(delay=1)
        return

    if message.content.startswith("s.t"):
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。VCチャンネルに接続してから、もう一度お試しください。")
            await message.delete(delay=1)
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
                for i in range(timer_int * 6):
                    await sleep(10)
                    await message.channel.send(str(counter) + "秒経過")
                    counter += 10
            embed = discord.Embed(title="TIME!")
            await message.channel.send(embed=embed)
            audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
            message.guild.voice_client.play(audio)
            return

    if message.content == "s.help":
        await message.channel.send("コマンド一覧\n`s.join` コマンドを打った人が居るVCチャンネルに接続\n`s.leave` VCチャンネルから切断\n`s.t` タイマーを利用できます。詳細はs.help timeと入力すると確認できます。\n`s.p count or s.count` 321beatboxの音声\n`s.p time or s.time` timeの音声\n`s.p kbbtime or s.kbbtime` 歓声無しtimeの音声 音源：KBB\n`s.p kansei or s.kansei` 歓声\n`s.p bunka or s.bunka` 文化の人の音声\n`s.p esh or s.esh` eshの音声\n`s.p msn or s.msn` make some noiseの音声\n`s.p olala or s.olala` olalaの音声")
        await message.channel.send("make some noise bot開発者：tari3210 #9924")
        await message.delete(delay=1)
        return

    if message.content == "s.help time":
        await message.channel.send("タイマー利用方法\n\n`s.t`の後ろに、半角スペースを空けて数字を入力してください。\n例：`s.t 3` \n1から10まで数字は分単位で、それ以上の数字は秒単位でセットされます。\n例1：1分40秒にセットしたい場合 `s.t 100`\n例2：3分にセットしたい場合 `s.t 3`もしくは`s.t 180`\n\n注意：必ず整数で入力してください。")
        await message.delete(delay=1)
        return

    if message.content == "s.c":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
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
        return

    if message.content == "s.c2":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.author.voice.channel.connect(reconnect=True)
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
            await message.author.voice.channel.connect(reconnect=True)
        names = [(j) for j in message.content.split()]
        if len(names) != 3:
            await message.channel.send("Error: 入力方法が間違っています。")
            return
        names.remove("s.battle")
        await message.channel.send(names[0] + "さん `1st` vs " + names[1] + "さん `2nd`\n\n1分・2ラウンドずつ\n1 minute, 2 rounds each\n\nAre you ready??")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("battle_start.mp3"), volume=0.5)
        message.guild.voice_client.play(audio)
        await sleep(12)
        await message.channel.send("3, 2, 1, Beatbox!")
        await sleep(3)
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("bunka.mp3"), volume=0)
        for i in range(4):
            await sleep(3)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            await sleep(6)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            await sleep(10)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            embed = discord.Embed(title="残り40秒", description="Round%s %s" % (str(i + 1), names[0]), color=0x00ff00)
            await message.channel.send(embed=embed)
            await sleep(10)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            await sleep(10)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            embed = discord.Embed(title="残り20秒", description="Round%s %s" % (str(i + 1), names[0]), color=0xffff00)
            await message.channel.send(embed=embed)
            await sleep(10)
            try:
                message.guild.voice_client.play(audio)
            except AttributeError:
                await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                return
            embed = discord.Embed(title="残り10秒", description="Round%s %s" % (str(i + 1), names[0]), color=0xff0000)
            await message.channel.send(embed=embed)
            await sleep(9)
            if i < 3:
                audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("round%sswitch.mp3" % (str(i + 2))), volume=1.5)
                try:
                    message.guild.voice_client.play(audio)
                except AttributeError:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                await message.channel.send("--------------------\n\nTIME!\nRound%s %s\nSWITCH!\n\n--------------------" % (str(i + 2), names[1]))
                names.reverse()
                await sleep(3)
            elif i == 3:
                audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("time.mp3"), volume=0.2)
                try:
                    message.guild.voice_client.play(audio)
                except AttributeError:
                    await message.channel.send("Error: 接続が失われたため、タイマーを停止しました\nlost connection")
                    return
                embed = discord.Embed(title="TIME!")
                await message.channel.send(embed=embed)
        embed = discord.Embed(title="投票箱", description="`1st:`%s\n`2nd:`%s\n\nぜひ気に入ったBeatboxerさんに1票をあげてみてください。\n※集計は行いません。botの動作はこれにて終了です。" % (names[1], names[0]))
        message3 = await message.channel.send(embed=embed)
        await message3.add_reaction("1⃣")
        await message3.add_reaction("2⃣")
        audio = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("msn.mp3"), volume=0.5)
        await sleep(3)
        message.guild.voice_client.play(audio)
        message4 = await message.channel.send("make some noise for the battle!\ncome on!!")
        await message4.add_reaction("🔥")
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
        await message.channel.send("処理中...")
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="battle stadium")
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        else:
            guild = client.get_guild(864475338340171786)  # サーバーID
            me = guild.get_member(896652783346917396)  # make some noise!
            await me.edit(suppress=False)
        channel0 = client.get_channel(930767329137143839)  # 対戦表
        await channel0.purge()
        role = message.guild.get_role(930368130906218526)  # battle stadium
        role_member = role.members
        for member in role_member:
            print(member.display_name + " をロールから削除")
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
        print("あと30秒で締め切ります。")
        await sleep(20)
        embed = discord.Embed(title="締め切り10秒前", color=0xff0000)
        await message.channel.send(embed=embed)
        print("締め切り10秒前")
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
        await channel0.send("%s\n %s を確認して、マイク設定を行ってからの参加をお願いします。" % (role.mention, bbx_mic.mention))
        return

    if message.content == "s.stage":
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        try:
            await stage_channel.create_instance(topic="battle stadium")
        except discord.errors.HTTPException:
            pass
        try:
            await stage_channel.connect(reconnect=True)
        except discord.errors.ClientException:
            pass
        guild = client.get_guild(864475338340171786)  # サーバーID
        me = guild.get_member(896652783346917396)  # make some noise!
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
                await message.channel.send("%sはビト森杯 A部門エントリー済み" % (name.display_name))
                return
            if role.id == 920321241976541204:  # B部門 ビト森杯
                await message.channel.send("%sはビト森杯 B部門エントリー済み" % (name.display_name))
                return
        await message.channel.send("%sはビト森杯にエントリーしていません" % (name.display_name))
        return

    if message.content == "s.end":
        stage_channel = client.get_channel(931462636019802123)  # ステージ
        await stage_channel.instance.delete()
        return

    if "s." not in message.content:
        if message.author.bot:
            return
        elif message.channel.id == 930447365536612353:
            await message.delete(delay=1)
        else:
            a = random.randint(1, 200)
            await sleep(2)
            if a == 1:
                await message.channel.send("ｵﾝｷﾞｬｱｱｱｱｱｱｱｱｱｱｱｱｱ！！！！！")
        return

client.run("ODk2NjUyNzgzMzQ2OTE3Mzk2.YWKO-g.PbWqRCFnvgd0YGAOMAHNqDKNQAU")
