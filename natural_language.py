import random
import re

from discord import ChannelType, Embed, Message

import database
from gbb import countdown, send_gbbinfo


async def natural_language(message: Message):

    # ビト森杯関連機能
    # プライベートスレッドはお問合せチャンネルなので除外
    if message.channel.type == ChannelType.private_thread:
        return

    # ビト森杯カテゴリーの場合除外
    if message.channel.category.name == "ビト森杯":
        return

    # GBB情報お知らせ機能
    if message.content.startswith("m!"):
        await send_gbbinfo(message)
        return

    # 以下おふざけリアクション機能・GBB情報お知らせ機能
    if "草" in message.content:
        emoji = message.guild.get_emoji(database.EMOJI_KUSA)
        await message.add_reaction(emoji)

    for word in ["💜❤💙💚", "brez", "ぶれず", "ブレズ", "愛", "sar", "oras", "かわいい", "カワイイ", "好", "impe", "いんぴ", "インピ", "ベッドタイムキャンディ"]:
        if word in message.content.lower():
            for stamp in ["💜", "❤", "💙", "💚"]:
                await message.add_reaction(stamp)

    embed = Embed(
        title="GBBの最新情報はこちら",
        description=">>> 以下のサイトにお探しの情報がない場合、\n__**未発表 もしくは 未定（そもそも決定すらしていない）**__\n可能性が非常に高いです。", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.onrender.com/")
    embed.add_field(name="swissbeatbox official instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    text = await countdown()
    embed.set_footer(text=text)

    # テキストチャンネルの場合
    if message.channel.type in [ChannelType.text, ChannelType.forum, ChannelType.public_thread, ChannelType.voice]:
        emoji = random.choice(message.guild.emojis)

        # Yuiにはbrezを
        if message.author.id in [database.YUI_1, database.YUI_2]:
            emoji = message.guild.get_emoji(database.EMOJI_BREZ)

        # 湯にはsaroを
        if message.author.id in [database.NURUYU_1, database.NURUYU_2]:
            emoji = message.guild.get_emoji(database.EMOJI_ORAS)

        # maycoにはheliumを
        if message.author.id in [database.MAYCO_1, database.MAYCO_2, database.MAYCO_3]:
            emoji = message.guild.get_emoji(database.EMOJI_HELIUM)

        await message.add_reaction(emoji)

        url_check = re.search(
            r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", message.content)
        if bool(url_check):
            return

        # GBBに関する言葉が含まれていたら、GBB情報を送信
        for word in ["gbb", "wildcard", "ワイカ", "ワイルドカード", "結果", "出場", "通過", "チケット", "ルール", "審査員", "ジャッジ", "日本人", "辞退", "キャンセル", "シード"]:
            if word in message.content.lower():
                if any(["?" in message.content, "？" in message.content]):
                    await message.reply("**GBB最新情報をお探しですか？**\n## ぜひこちらのサイトをご覧ください！\n\n[GBBINFO-JPN 日本非公式情報サイト](https://gbbinfo-jpn.onrender.com/)")
                    await message.reply(embed=embed)
                else:
                    await message.channel.send(embed=embed)
                break
    return
