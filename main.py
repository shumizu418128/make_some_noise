import os
import random
from asyncio import sleep
from datetime import datetime, timedelta, timezone

import discord
from discord import (Client, Embed, EventStatus, File, Intents, Interaction,
                     Member, Message, PrivacyLevel, VoiceState)
from discord.errors import ClientException

from advertise import advertise
from battle_stadium import battle, start
from button_callback import (button_accept_replace, button_call_admin,
                             button_cancel, button_contact, button_entry,
                             button_submission_content)
from gbb_countdown import gbb_countdown
from keep_alive import keep_alive
from natural_language import natural_language
from search_next_event import search_next_event

# from daily_work import daily_work

# NOTE: ビト森杯運営機能搭載ファイル
TOKEN = os.environ['DISCORD_BOT_TOKEN']
intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
print(f"Make Some Noise! (server): {discord.__version__}")

JST = timezone(timedelta(hours=9))


@client.event
async def on_ready():  # 起動時に動作する処理
    advertise.start(client)  # バトスタ宣伝、バトスタ開始ボタン
    # TODO エントリー開始時、有効化
    # daily_work.start(client)  # ビト森杯定期作業
    return


@client.event
async def on_interaction(interaction: Interaction):
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    custom_id = interaction.data["custom_id"]

    # interaction通知
    embed = Embed(
        title=custom_id,
        description=f"{interaction.user.mention}\n{interaction.message.jump_url}",
        color=0x00bfff
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await bot_channel.send(f"{interaction.user.id}", embed=embed)

    ##############################
    # 参加者が押すボタン
    ##############################

    # ビト森杯エントリー
    if custom_id.startswith("button_entry"):
        await button_entry(interaction)

    # お問い合わせ
    if custom_id == "button_contact":
        await button_contact(interaction)

    # 運営呼び出し
    if custom_id == "button_call_admin":
        await button_call_admin(interaction)

    # キャンセル
    if custom_id == "button_cancel":
        await button_cancel(interaction)

    # エントリー状況照会
    if custom_id == "button_submission_content":
        await button_submission_content(interaction)

    # 繰り上げエントリー
    if custom_id == "button_accept_replace":
        await button_accept_replace(interaction)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == 412082841829113877 or member.bot:  # tari3210
        return
    try:
        vc_role = member.guild.get_role(935073171462307881)  # in a vc
        if bool(before.channel) and after.channel is None:  # チャンネルから退出
            await member.remove_roles(vc_role)
        # チャンネルに参加
        elif before.channel != after.channel and bool(after.channel):
            embed = Embed(title="BEATBOXをもっと楽しむために",
                          description="", color=0x0081f0)
            embed.add_field(name=f"Let's show your 💜❤💙💚 with `{member.display_name}`!",
                            value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。")
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森", icon_url=member.guild.icon.url)
            if after.channel.id == 886099822770290748:  # リアタイ部屋
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", embed=embed, delete_after=60)
            else:
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", delete_after=60)
            await member.add_roles(vc_role)
    except Exception:
        return


@client.event
async def on_member_join(member: Member):
    channel = client.get_channel(864475338340171791)  # 全体チャット
    await sleep(2)
    embed_discord = Embed(
        title="Discordの使い方", description="https://note.com/me1o_crew/n/nf2971acd1f1a")
    embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    text = await gbb_countdown()  # GBBまでのカウントダウン
    embed.set_footer(text=text)
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event):
        await sleep(1)
        await channel.send(next_event.url)

    # TODO エントリー開始時、有効化
    """view = await get_view_contact(entry=True, contact=True)
    await channel.send("第3回ビト森杯・Online Loopstation Exhibition Battle", view=view)"""


@client.event
async def on_message(message: Message):
    # バトスタ対戦表、バトスタチャット
    if message.author.bot or message.content.startswith("l.") or message.channel.id in [930767329137143839, 930839018671837184]:
        return
    # s.から始まらない場合(コマンドではない場合)
    if not message.content.startswith("s."):
        await natural_language(message)
        """if message.channel.id == 1035965200341401600:  # ビト森杯 お知らせ
            view == await get_view(entry=True, contact=True)
            await message.channel.send(view=view)
        """
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    # TODO エントリー開始時、有効化
    """if message.content == "s.loop":
        await message.delete(delay=1)
        announce = client.get_channel(
            1035965200341401600  # ビト森杯 お知らせ
        )
        bot_notice_channel = client.get_channel(
            916608669221806100  # ビト森杯 進行bot
        )
        contact = client.get_channel(
            1035964918198960128  # 問い合わせ
        )
        view = await get_view(entry=True, contact=True)
        await announce.send("第3回ビト森杯・Online Loopstation Exhibition Battle", view=view)
        """

    # VS参加・退出
    if message.content == "s.join":
        await message.delete(delay=1)
        if message.author.voice is None:
            await message.channel.send("VCチャンネルに接続してから、もう一度お試しください。")
            return
        try:
            await message.author.voice.channel.connect(reconnect=True)
        except ClientException:
            await message.channel.send("既に接続しています。\nチャンネルを移動させたい場合、一度切断してからもう一度お試しください。")
            return
        else:
            await message.channel.send("接続しました。")
            return

    if message.content == "s.leave":
        await message.delete(delay=1)
        if message.guild.voice_client is None:
            await message.channel.send("接続していません。")
            return
        await message.guild.voice_client.disconnect()
        await message.channel.send("切断しました。")
        return

    ##############################
    # バトスタコマンド
    ##############################

    if message.content.startswith("s.battle"):
        await battle(message.content, client)
        return

    if message.content == "s.start":
        await start(client)
        return

    if message.content == "s.end":
        await message.delete(delay=1)
        pairing_channel = client.get_channel(930767329137143839)  # 対戦表
        bs_role = message.guild.get_role(930368130906218526)  # BATTLE STADIUM
        stage = client.get_channel(931462636019802123)  # ステージ
        scheduled_events = message.guild.scheduled_events
        for scheduled_event in scheduled_events:
            if scheduled_event.status == EventStatus.active and scheduled_event.name == "BATTLE STADIUM":
                await scheduled_event.end()
        try:
            instance = await stage.fetch_instance()
        except Exception:
            pass
        else:
            await instance.delete()
        await pairing_channel.purge()
        for member in bs_role.members:
            await member.remove_roles(bs_role)
        return

    # 今週末のバトスタを設定（2週間後ではない）
    if message.content.startswith("s.bs"):
        general = message.guild.get_channel(864475338340171791)  # 全体チャット
        announce = message.guild.get_channel(885462548055461898)  # お知らせ
        await message.delete(delay=1)
        dt_now = datetime.now(JST)
        sat = timedelta(days=6 - int(dt_now.strftime("%w")))
        start_time = datetime(dt_now.year, dt_now.month,
                              dt_now.day, 21, 30, 0, 0, JST) + sat
        end_time = datetime(dt_now.year, dt_now.month,
                            dt_now.day, 22, 30, 0, 0, JST) + sat
        stage = client.get_channel(931462636019802123)  # BATTLE STADIUM
        event = await message.guild.create_scheduled_event(
            name="BATTLE STADIUM",
            description="【エキシビションBeatboxバトルイベント】\n今週もやります！いつでも何回でも参加可能です。\nぜひご参加ください！\n観戦も可能です。観戦中、マイクがオンになることはありません。\n\n※エントリー受付・当日の進行はすべてbotが行います。\n※エントリー受付開始時間は、バトル開始1分前です。",
            start_time=start_time,
            end_time=end_time,
            channel=stage,
            privacy_level=PrivacyLevel.guild_only)
        await announce.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
        await announce.send(event.url)
        await general.send(file=File(f"battle_stadium_{random.randint(1, 3)}.gif"))
        await general.send(event.url)
        return

keep_alive()
try:
    client.run(TOKEN)
except Exception:
    os.system("kill 1")
