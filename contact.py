
from datetime import timedelta, timezone

import gspread_asyncio
from discord import ButtonStyle, Client, Embed, Intents, Interaction, Member
from discord.ui import Button, View
from oauth2client.service_account import ServiceAccountCredentials

from entry_cancel import entry_cancel, entry_replacement

"""
search_contact: ユーザーの問い合わせスレッドを取得もしくは作成(createのboolで選択)
get_view_contact: 問い合わせボタンのViewを取得(エントリー状況に応じてボタンを変更)
contact_start: 問い合わせを開始
button_contact: 問い合わせボタン（search_contactで作成して、contact_startで開始）

button_call_admin: 運営呼び出しボタン
button_cancel: キャンセルボタン
button_entry_confirm: エントリー状況照会ボタン
"""

intents = Intents.all()  # デフォルトのIntentsオブジェクトを生成
intents.typing = False  # typingを受け取らないように
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff
JST = timezone(timedelta(hours=9))

"""
Google spreadsheet
row = 縦 1, 2, 3, ...
col = 横 A, B, C, ...
"""


def get_credits():
    return ServiceAccountCredentials.from_json_keyfile_name(
        "makesomenoise-4cb78ac4f8b5.json",
        ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets'])


async def search_contact(member: Member, create: bool = False, locale: str = "ja"):
    contact = member.guild.get_channel(
        1035964918198960128  # 問い合わせ
    )
    threads = contact.threads  # 問い合わせスレッド一覧
    # スレッド名一覧 (member.id)_(locale)
    thread_names = [thread.name.split("_")[0] for thread in threads]

    # 問い合わせスレッドがすでにある場合
    if str(member.id) in thread_names:
        index = thread_names.index(str(member.id))
        return threads[index]

    # 問い合わせスレッドがなく、作成しない場合
    if create is False:
        return None

    # 問い合わせスレッドがなく、作成する場合
    thread = await contact.create_thread(name=f"{member.id}_{locale}")
    return thread


async def get_view_contact(entry: bool):
    button_call_admin = Button(
        label="ビト森杯運営に問い合わせ",
        style=ButtonStyle.primary,
        custom_id="button_call_admin",
        emoji="📩"
    )
    button_cancel = Button(
        label="エントリーキャンセル",
        style=ButtonStyle.red,
        custom_id="button_cancel",
        emoji="❌"
    )
    button_entry_confirm = Button(
        label="エントリー状況照会",
        style=ButtonStyle.gray,
        custom_id="button_entry_confirm",
        emoji="🔍"
    )
    button_entry = Button(
        style=ButtonStyle.green,
        label="エントリー",
        custom_id="button_entry",
        emoji="✅"
    )
    view = View(timeout=None)
    view.add_item(button_call_admin)
    view.add_item(button_entry_confirm)
    if entry:  # エントリーしている場合
        view.add_item(button_cancel)
    else:  # エントリーしていない場合
        view.add_item(button_entry)
    return view


async def contact_start(client: Client, member: Member, entry_redirect: bool = False):
    # 問い合わせスレッドを取得 リダイレクトならスレッド作成
    thread = await search_contact(member, create=entry_redirect)
    contact = thread.guild.get_channel(
        1035964918198960128  # 問い合わせ
    )
    announce = thread.guild.get_channel(
        1035965200341401600  # ビト森杯お知らせ
    )
    admin = thread.guild.get_role(
        904368977092964352  # ビト森杯運営
    )
    locale = thread.name.split("_")[1]  # スレッド名からlocaleを取得

    # 最初は喋るな
    await contact.set_permissions(member, send_messages_in_threads=False)

    # 日本語アクセスの場合
    if locale == "ja":
        embed = Embed(
            title="お問い合わせの前に",
            description=f"ビト森杯の情報は\n{announce.mention}\nに掲載されています。\
                \n\nこれらの内容を必ずご確認ください。もし、ご質問がありましたら\n「ビト森杯運営に問い合わせ」ボタンを押してください。運営が対応します。",
            color=yellow
        )
        role_check = [
            member.get_role(
                1036149651847524393  # ビト森杯
            ),
            member.get_role(
                1172542396597289093  # キャンセル待ち ビト森杯
            )
        ]
        if any(role_check):  # エントリーしている場合
            view = await get_view_contact(entry=True)
        else:  # エントリーしていない場合
            view = await get_view_contact(entry=False)
        await thread.send(f"ここは {member.mention} さん専用のお問い合わせチャンネルです。", embed=embed, view=view)
        return

    # 海外アクセスの場合
    else:
        embed_overseas = Embed(  # 通常の問い合わせ
            title="Please write your inquiry here",
            description="請把疑問寫在這裡\n문의 내용을 이 채널에 기입해주세요",
            color=blue
        )
        if entry_redirect:  # 海外エントリー時の問い合わせリダイレクトの場合
            embed_overseas = Embed(
                title="海外からのエントリー",
                description="Please hold on, the moderator will be here soon\
                    \n請稍候片刻, 正與管理員對接\n대회 운영자가 대응합니다. 잠시 기다려주십시오",
                color=blue
            )
        embed_jp = Embed(
            description=f"{member.display_name}さんのDiscord言語設定が日本語ではなかったため、海外対応モードになっています。\
                \n日本語対応をご希望の場合、このチャンネルに\n\n**日本語希望**\n\nとご記入ください。\n自動で日本語対応に切り替わります。"
        )
        embed_jp.set_footer(text=f"ISO 639-1 code: {locale}")

        # 問い合わせスレッドにメンション付きで送信
        await thread.send(f"{member.mention}", embeds=[embed_overseas, embed_jp])
        await thread.send(f"{admin.mention}\n海外対応モード")

        # しゃべってよし
        await contact.set_permissions(member, send_messages_in_threads=True)

        def check(m):
            return m.channel == thread and m.content == "日本語希望"

        _ = await client.wait_for('message', check=check)

        """
        日本語モードへ変更
        """

        # スレッド名を日本語モードへ変更
        await thread.edit(name=f"{member.id}_ja")
        embed = Embed(
            title="大変失礼しました",
            description="今後、日本語モードで対応いたします。",
            color=blue)

        # エントリー時の問い合わせリダイレクトの場合
        if entry_redirect:
            embed.description += "\n\n以下のボタンからエントリーしてください。"
            button = Button(
                style=ButtonStyle.green,
                label="エントリー",
                custom_id="button_entry",
                emoji="✅")
            view = View(timeout=None)
            view.add_item(button)
            await thread.send(member.mention, embed=embed, view=view)

        # 通常の問い合わせ
        else:
            await thread.send(member.mention, embed=embed)
            await contact_start(client, member)
        return


async def button_contact(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))
    embed = Embed(
        title="お問い合わせチャンネル作成",
        description=f"{thread.jump_url} までお問い合わせください。",
        color=0x00bfff
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    await contact_start(client=interaction.client, member=interaction.user)


async def button_call_admin(interaction: Interaction):
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
    )
    admin = interaction.user.get_role(
        904368977092964352  # ビト森杯運営
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = interaction.guild.get_member(
        412082841829113877
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )

    role_check = [
        interaction.user.get_role(
            1036149651847524393  # ビト森杯
        ),
        interaction.user.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
    ]

    # しゃべってよし
    await contact.set_permissions(interaction.user, send_messages_in_threads=True)

    embed = Embed(
        title="このチャンネルにご用件をご記入ください",
        description="運営メンバーが対応します",
        color=blue
    )
    await interaction.response.send_message(f"{admin.mention}\n{interaction.user.mention}", embed=embed)

    # どちらのロールも持っている場合（異常なロール付与）
    if all(role_check):
        await bot_channel.send(f"{tari3210.mention}\nbutton_entry_check Error: 重複ロール付与\n\n{interaction.channel.jump_url}")
        return

    # エントリー状況確認（正常）
    if not any(role_check):  # エントリーしていない
        embed = Embed(
            title="エントリー状況",
            description=f"{interaction.user.display_name}さんはビト森杯にエントリーしていません。"
        )
        await interaction.channel.send(embed=embed)
        return

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # DBから取得
    cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索

    # DB登録なし
    if bool(cell_id) is False:
        await bot_channel.send(f"{tari3210.mention}\nbutton_entry_info Error: DB登録なし\n\n{interaction.channel.jump_url}")
        return

    # DB登録あり
    cell_values = await worksheet.row_values(cell_id.row)  # ユーザーIDの行の値を取得
    cell_values = cell_values[2:9]

    if role_check[1]:  # キャンセル待ちの場合、何番目かを取得
        # キャンセル待ちの順番最初の人を取得
        cell_wait_first = await worksheet.find("キャンセル待ち", in_column=5)

        # キャンセル待ちの順番を取得
        cell_waitlist_position = cell_id.row - cell_wait_first.row + 1
        cell_values[2] += f" {len(role_reserve)}人中 {cell_waitlist_position}番目"

    embed = Embed(
        title=f"{interaction.user.display_name}さん エントリー状況 詳細",
        description=f"- 名前: {cell_values[0]}\n- 読み: {cell_values[1]}\n- 出場可否: {cell_values[2]}\
            \n- デバイス: {cell_values[3]}\n- 備考: {cell_values[4]}\n- 受付時刻: {cell_values[5]}"
    )
    await interaction.channel.send(embed=embed)
    return


async def button_cancel(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
    )

    # 喋るな(スレッドでキャンセルしている前提)
    await contact.set_permissions(interaction.user, send_messages_in_threads=False)

    # そもそもエントリーしてる？
    role_check = [
        interaction.user.get_role(
            1036149651847524393  # ビト森杯
        ),
        interaction.user.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
    ]
    if not any(role_check):  # どちらのロールも持っていない場合
        embed = Embed(
            title="エントリーキャンセル",
            description=f"Error: {interaction.user.display_name}さんはビト森杯にエントリーしていません。",
            color=red
        )
        await interaction.followup.send(embed=embed)
        return

    # キャンセル意思の最終確認
    embed = Embed(
        title="エントリーキャンセル",
        description="ビト森杯エントリーをキャンセルしますか？\n⭕ `OK`\n❌ このメッセージを削除する",
        color=yellow
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    notice = await interaction.followup.send(embed=embed)
    await notice.add_reaction("⭕")
    await notice.add_reaction("❌")

    def check(reaction, user):
        return user == interaction.user and reaction.emoji in ["⭕", "❌"] and reaction.message == notice

    try:
        reaction, _ = await interaction.client.wait_for('reaction_add', timeout=10, check=check)
    except TimeoutError:  # 10秒で処理中止
        await notice.clear_reactions()
        await notice.reply("Error: Timeout\nもう1度お試しください")
        return
    await notice.clear_reactions()
    if reaction.emoji == "❌":  # ❌ならさよなら
        await notice.delete(delay=1)
        return

    await entry_cancel(interaction.user)
    await entry_replacement(interaction.client)


async def button_entry_confirm(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
    )

    # 喋るな(スレッドでボタン押してる前提)
    await contact.set_permissions(interaction.user, send_messages_in_threads=False)

    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = interaction.guild.get_member(
        412082841829113877
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )

    role_check = [
        interaction.user.get_role(
            1036149651847524393  # ビト森杯
        ),
        interaction.user.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
    ]

    # どちらのロールも持っている場合（異常なロール付与）
    if all(role_check):
        embed = Embed(
            title="エントリー状況照会",
            description="Error: 運営が対処しますので、しばらくお待ちください。",
            color=red
        )
        await interaction.followup.send(embed=embed)
        await bot_channel.send(f"{tari3210.mention}\nbutton_entry_check Error: 重複ロール付与\n\n{interaction.channel.jump_url}")
        return

    # エントリー状況確認（正常）
    if not any(role_check):  # エントリーしていない
        embed = Embed(
            title="エントリー状況照会",
            description=f"{interaction.user.display_name}さんはビト森杯にエントリーしていません。"
        )
        await interaction.followup.send(embed=embed)
        return

    if role_check[0]:  # ビト森杯
        embed = Embed(
            title="エントリー状況照会",
            description=f"{interaction.user.display_name}さんはビト森杯にエントリー済みです。",
            color=green
        )
    if role_check[1]:  # キャンセル待ち ビト森杯
        embed = Embed(
            title="エントリー状況照会",
            description=f"{interaction.user.display_name}さんはビト森杯キャンセル待ち登録済みです。",
            color=green
        )

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # DBから取得
    cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索

    # DB登録なし
    if bool(cell_id) is False:
        embed = Embed(
            title="エントリー状況照会 詳細情報",
            description="Error: エントリー詳細情報の取得に失敗しました。\n運営が対処しますので、しばらくお待ちください。",
            color=red
        )
        await interaction.channel.send(embed=embed)
        await bot_channel.send(f"{tari3210.mention}\nbutton_entry_info Error: DB登録なし\n\n{interaction.channel.jump_url}")
        return

    # DB登録あり
    cell_values = await worksheet.row_values(cell_id.row)  # ユーザーIDの行の値を取得
    cell_values = cell_values[2:9]

    if role_check[1]:  # キャンセル待ちの場合、何番目かを取得
        # キャンセル待ちの順番最初の人を取得
        cell_wait_first = await worksheet.find("キャンセル待ち", in_column=5)

        # キャンセル待ちの順番を取得
        cell_waitlist_position = cell_id.row - cell_wait_first.row + 1
        cell_values[2] += f" {len(role_reserve)}人中 {cell_waitlist_position}番目"

    embed = Embed(
        title=f"エントリー状況照会 詳細情報",
        description=f"- 名前: {cell_values[0]}\n- 読み: {cell_values[1]}\n- 出場可否: {cell_values[2]}\
            \n- デバイス: {cell_values[3]}\n- 備考: {cell_values[4]}\n- 受付時刻: {cell_values[5]}"
    )
    await interaction.channel.send(embed=embed)
