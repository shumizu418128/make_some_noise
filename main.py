import os
from asyncio import sleep
from datetime import datetime, timedelta, timezone

import discord
from discord import Client, Embed, Intents, Member, Message, VoiceState
from discord.errors import ClientException

from advertise import advertise
from battle_stadium import battle, start

"""
from button_admin_callback import (button_admin_cancel,
                                   button_admin_create_thread,
                                   button_admin_entry,
                                   button_admin_submission_content)
from button_callback import (button_call_admin, button_cancel, button_contact,
                             button_submission_content, button_accept_replace, button_entry)
from button_view import get_view
from daily_work import daily_work_AM9, daily_work_PM10
"""
import database
from gbb import countdown
from keep_alive import keep_alive
from natural_language import natural_language
from search_next_event import search_next_event

# NOTE: ビト森杯運営機能搭載ファイル
TOKEN = os.environ['DISCORD_BOT_TOKEN']
intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
client = Client(intents=intents)
JST = timezone(timedelta(hours=9))

print(
    f"Make Some Noise! (server): {discord.__version__} {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')}")


@client.event
async def on_ready():  # 起動時に動作する処理
    advertise.start(client)  # バトスタ宣伝、バトスタ開始ボタン
    # daily_work_PM10.start(client)  # ビト森杯定期作業 22:00
    # daily_work_AM9.start(client)  # ビト森杯定期作業 09:00
    return


# TODO: 第4回ビト森杯実装
# A, B, Loop部門のエントリー受付
# モーダルの処理を追加
"""@client.event
async def on_interaction(interaction: Interaction):
    bot_channel = interaction.guild.get_channel(database.CHANNEL_BOT)
    custom_id = interaction.data["custom_id"]

    # ボタンのカスタムIDに_がない場合、custom_id未設定のためreturn
    if "_" not in custom_id:
        return

    # セレクトメニューの場合
    # いったん凍結
    if custom_id.startswith("select"):
        await interaction.response.defer(ephemeral=True, thinking=True)
        value = interaction.data["values"][0]
        await interaction.followup.send(
            interaction.user.mention,
            file=File(f"{value}.jpg"),
            ephemeral=True
        )
        return

    # モーダルの場合、エントリー処理 (callback.pyに移動)
    if custom_id.startswith("modal"):
        await modal_callback(interaction)
        return

    ##############################
    # 運営専用ボタン
    ##############################

    role_check = interaction.user.get_role(database.ROLE_ADMIN)
    if bool(role_check):

        # ビト森杯エントリー
        if "entry" in custom_id:
            await button_admin_entry(interaction)

        # キャンセル
        if "cancel" in custom_id:
            await button_admin_cancel(interaction)

        # エントリー状況照会
        if "submission_content" in custom_id:
            await button_admin_submission_content(interaction)

        # 問い合わせスレッド作成
        if custom_id == "button_admin_create_thread":
            await button_admin_create_thread(interaction)

    ###################
    # 参加者が押すボタン
    ###################

    else:
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

    ###################
    # interaction通知
    ###################

    embed = Embed(
        title=custom_id,
        description=f"{interaction.user.mention}\nmessage: {interaction.message.jump_url}",
        color=0x00bfff
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = datetime.now(JST)

    # 問い合わせスレッドがあり、かつ該当interactionと別チャンネルなら、descriptionに追加
    thread = await search_contact(interaction.user)
    if bool(thread) and interaction.message.channel.id != thread.id:
        embed.description += f"\n\ncontact: {thread.jump_url}"

    # ない場合その旨を表示
    if bool(thread) is False:
        embed.description += "\n\ncontact: なし"

    # サイレントで送信 ユーザーに通知しない
    await bot_channel.send(f"{interaction.user.id}", embed=embed, silent=True)
"""


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if member.id == database.TARI3210 or member.bot:
        return
    try:
        vc_role = member.guild.get_role(database.ROLE_VC)

        # チャンネルから退出
        if bool(before.channel) and after.channel is None:
            await member.remove_roles(vc_role)

        # チャンネルに参加
        elif before.channel != after.channel and bool(after.channel):
            embed = Embed(
                title="BEATBOXをもっと楽しむために",
                description="", color=0x0081f0
            )
            embed.add_field(
                name=f"Let's show your 💜❤💙💚 with {member.display_name}!",
                value="ビト森のすべての仲間たちと、\nもっとBEATBOXを好きになれる。\nそんなあたたかい雰囲気作りに、\nぜひ、ご協力をお願いします。"
            )
            embed.set_footer(
                text="We love beatbox, We are beatbox family\nあつまれ！ビートボックスの森",
                icon_url=member.guild.icon.url
            )
            if after.channel.id == database.VC_REALTIME:  # リアタイ部屋
                content = f"{member.mention} チャットはこちら chat is here"

                # マイクオンの場合、通知する
                if after.self_mute is False:
                    content += f"\n{member.display_name}さんはマイクがONになっています。ミュートに設定を変更すると、聞き専参加が可能です。"

                # マイクオフの場合、オンにすることを推奨する
                elif after.self_mute is True:
                    content += f"\n{member.display_name}さんはマイクがOFFになっています。ぜひマイクをONにして、一緒に盛り上がりましょう！"

                await after.channel.send(content, embed=embed, delete_after=60)

            else:
                await after.channel.send(f"{member.mention} チャットはこちら chat is here", delete_after=60)

            await member.add_roles(vc_role)
    except Exception:
        return


@client.event
async def on_member_join(member: Member):
    channel = client.get_channel(database.CHANNEL_GENERAL)
    await sleep(2)
    embed_discord = Embed(
        title="Discordの使い方", description="https://note.com/me1o_crew/n/nf2971acd1f1a")
    embed = Embed(title="GBBの最新情報はこちら", color=0xF0632F)
    embed.add_field(name="GBBINFO-JPN 日本非公式情報サイト",
                    value="https://gbbinfo-jpn.jimdofree.com/")
    embed.add_field(name="swissbeatbox 公式instagram",
                    value="https://www.instagram.com/swissbeatbox/")
    text = await countdown()  # GBBまでのカウントダウン
    embed.set_footer(text=text)
    await channel.send(f"{member.mention}\nあつまれ！ビートボックスの森 へようこそ！", embeds=[embed_discord, embed])
    next_event = await search_next_event(channel.guild.scheduled_events)
    if bool(next_event):
        await sleep(1)
        await channel.send(next_event.url)


@client.event
async def on_message(message: Message):
    # バトスタ対戦表、バトスタチャット
    """if message.author.bot or message.content.startswith("l.") or message.channel.id in [930767329137143839, 930839018671837184]:
        return"""

    # s.から始まらない場合(コマンドではない場合)
    if not message.content.startswith("s."):
        await natural_language(message)
        return

    if message.content == "s.test":
        await message.channel.send(f"{str(client.user)}\n{discord.__version__}")
        return

    # vcのroleメンバーを削除
    if message.content == "s.clear":
        vc_role = message.guild.get_role(database.ROLE_VC)
        for member in vc_role.members:
            await member.remove_roles(vc_role)
        return

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
"""
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
        return"""

keep_alive()
try:
    client.run(TOKEN)
except Exception:
    os.system("kill 1")
