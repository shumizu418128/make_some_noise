import random
import re

from discord import ChannelType, Embed, Message

from gbb import countdown, send_gbbinfo


async def natural_language(message: Message):
    if message.channel.type == ChannelType.private_thread:
        return

    if message.channel.category.name == "ビト森杯":
        return

    if message.content.startswith("m!"):
        await send_gbbinfo(message)
        return

    if "草" in message.content:
        emoji = message.guild.get_emoji(990222099744432198)  # 草
        await message.add_reaction(emoji)

    for word in ["💜❤💙💚", "brez", "ぶれず", "ブレズ", "愛", "sar", "oras", "かわいい", "カワイイ", "好", "impe", "いんぴ", "インピ", "ベッドタイムキャンディ"]:
        if word in message.content.lower():
            for stamp in ["💜", "❤", "💙", "💚"]:
                await message.add_reaction(stamp)

    embed = Embed(
        title="GBBの最新情報はこちら",
        description=">>> 以下のサイトにお探しの情報がない場合、\n__**未発表 もしくは 未定（そもそも決定すらしていない）**__\n可能性が非常に高いです。", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    text = await countdown()
    embed.set_footer(text=text)

    if "m!wc" in message.content.lower():
        await message.channel.send(embed=embed)
        await message.channel.send("[GBB 2023 Wildcard結果・出場者一覧 はこちら](https://gbbinfo-jpn.jimdofree.com/20230222/)")

    # テキストチャンネルの場合
    if message.channel.type in [ChannelType.text, ChannelType.forum, ChannelType.public_thread]:
        emoji = random.choice(message.guild.emojis)

        # Yuiにはbrezを
        if message.author.id in [891228765022195723, 886518627023613962]:
            emoji = message.guild.get_emoji(889877286055198731)  # brez

        # 湯にはsaroを
        if message.author.id in [887328590407032852, 870434043810971659]:
            emoji = message.guild.get_emoji(889920546408661032)  # oras

        # maycoにはheliumを
        if message.author.id in [389427133099016193, 735099594010132480, 990630026275860540]:
            emoji = message.guild.get_emoji(890506350868721664)  # helium

        await message.add_reaction(emoji)

        url_check = re.search(
            r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", message.content)
        if bool(url_check):
            return

        for word in ["gbb", "wildcard", "ワイカ", "ワイルドカード", "結果", "出場", "通過", "チケット", "ルール", "審査員", "ジャッジ", "日本人", "colaps"]:
            if word in message.content.lower():
                if any(["?" in message.content, "？" in message.content]):
                    await message.reply("**GBB最新情報をお探しですか？**\n## ぜひこちらのサイトをご覧ください！\n\n[GBBINFO-JPN 日本非公式情報サイト](https://gbbinfo-jpn.jimdofree.com/)")
                    await message.reply(embed=embed)
                else:
                    await message.channel.send(embed=embed)
                break
    return
