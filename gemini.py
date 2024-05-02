from asyncio import sleep
from contact import debug_log, get_submission_embed
import database
import os
from discord import Interaction, Message
import google.generativeai as genai


async def setup():
    """
    Geminiの初期設定を行う関数
    return: chat
    """

    safety_settings = database.SAFETY_SETTINGS
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel(
        model_name='gemini-pro',
        safety_settings=safety_settings
    )
    chat = model.start_chat()
    return chat


async def send_message(chat: genai.ChatSession, message: Message):
    """
    メッセージを送信する関数
    chat: chat
    message: Message
    return: chat or None
    """
    # messageを送信 20回まで試行
    for _ in range(20):
        try:
            response = chat.send_message_async(message.content)

        # 送信失敗したら15秒待って再送
        except Exception as e:
            await sleep(15)
            print("メッセージ送信失敗: 再送します")
            print(e)
            continue
        else:
            return response

    # 20回送信しても失敗したら、運営対応に切り替えてNoneを返す
    else:
        await call_admin(message)
        return None


async def call_admin(message: Message, *, interaction=Interaction):
    """
    Gemini対応を終了し、運営に通知する関数
    message: Message
    return: None
    """
    admin = message.guild.get_member(database.ROLE_ADMIN)
    contact = message.guild.get_channel(database.CHANNEL_CONTACT)

    # 運営へ通知
    await message.reply(
        f"{admin.mention}\n{message.author.display_name}さんからの問い合わせ",
        mention_author=False
    )
    # エントリー状況照会
    embed = await get_submission_embed(message.author)

    # interactionがある場合は、interactionに返信
    if bool(interaction):
        await interaction.response.send_message(embed=embed)
    else:
        await message.channel.send(embed=embed)

    # しゃべってよし
    await contact.set_permissions(message.author, send_messages_in_threads=True)

    await debug_log(
        "fail_response",
        "AIとの通信に失敗しました",
        0xff0000,
        message.author
    )
    return
