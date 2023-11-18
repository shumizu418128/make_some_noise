from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Embed, Interaction
from oauth2client.service_account import ServiceAccountCredentials

from contact import contact_start, search_contact
from entry import entry_cancel, modal_entry

JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff

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


async def button_entry(interaction: Interaction):
    dt_now = datetime.now(JST)
    dt_entry_start = datetime(
        year=2024,
        month=1,
        day=6,
        tzinfo=JST
    )
    # エントリー開始時刻確認
    if dt_now < dt_entry_start:
        await interaction.response.send_message(
            "エントリー受付開始は1月6日です。",
            ephemeral=True)
        return

    # 問い合わせ確認
    locale = str(interaction.locale)
    thread = await search_contact(member=interaction.user, create=False, locale=str(interaction.locale))
    if bool(thread):  # 問い合わせスレッドあり
        locale = thread.name.split("_")[1]

    # 日本からのエントリー
    if locale == "ja":
        await interaction.response.send_modal(modal_entry(interaction.user.display_name))
        return

    # 海外からのエントリー
    else:
        await interaction.response.defer(ephemeral=True)
        thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))

        if str(interaction.locale) == "zh-TW":  # 台湾
            embed = Embed(
                title="contact required: access from overseas",
                description=f"錯誤：請點一下 {thread.mention} 聯係我們\
                    \nお手数ですが {thread.mention} までお問い合わせください。",
                color=red
            )
        elif str(interaction.locale) == "zh-CN":  # 中国
            embed = Embed(
                title="contact required: access from overseas",
                description=f"错误：请点击 {thread.mention} 联系我们\
                    \nお手数ですが {thread.mention} までお問い合わせください。",
                color=red
            )
        elif str(interaction.locale) == "ko":  # 韓国
            embed = Embed(
                title="contact required: access from overseas",
                description=f"문의는 {thread.mention} 로 보내주세요\
                    \nお手数ですが {thread.mention} までお問い合わせください。",
                color=red
            )
        else:  # 英語
            embed = Embed(
                title="contact required: access from overseas",
                description=f"please contact us via {thread.mention}\
                    \nお手数ですが {thread.mention} までお問い合わせください。",
                color=red
            )
        await interaction.followup.send(embed=embed, ephemeral=True)
        await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


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


# TODO: 動作テスト
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


# TODO: entry_cancelの動作テスト
async def button_cancel(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
    )
    role_check = [
        interaction.user.get_role(
            1036149651847524393  # ビト森杯
        ),
        interaction.user.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
    ]

    # 喋るな(スレッドでキャンセルしている前提)
    await contact.set_permissions(interaction.user, send_messages_in_threads=False)

    # そもそもエントリーしてる？
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


# TODO: 動作テスト
async def button_entry_confirm(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
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

    # 喋るな(スレッドでボタン押してる前提)
    await contact.set_permissions(interaction.user, send_messages_in_threads=False)

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
        title="エントリー状況照会 詳細情報",
        description=f"- 名前: {cell_values[0]}\n- 読み: {cell_values[1]}\n- 出場可否: {cell_values[2]}\
            \n- デバイス: {cell_values[3]}\n- 備考: {cell_values[4]}\n- 受付時刻: {cell_values[5]}"
    )
    await interaction.channel.send(embed=embed)


async def button_accept_replace(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    role = interaction.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )

    embed = Embed(
        title="繰り上げ出場手続き完了",
        description="手続きが完了しました。",
        color=green
    )
    await interaction.followup.send(embed=embed)  # 通知

    # ロール付け替え
    await interaction.user.remove_roles(role_reserve)
    await interaction.user.add_roles(role)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # DB更新
    cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索
    await worksheet.update_cell(cell_id.row, 5, "出場")  # 出場可否を出場に変更
    await worksheet.update_cell(cell_id.row, 10, "")  # 繰り上げ手続き締切を削除

    # 時間を追記
    cell_time = await worksheet.cell(row=cell_id.row, col=8)
    await worksheet.update_cell(
        row=cell_time.row,
        col=cell_time.col,
        value=cell_time.value + " 繰り上げ: " +
        datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    )

    # 通知
    embed = Embed(
        title="繰り上げ出場手続き完了",
        description=interaction.channel.jump_url,
        color=green)
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url
    )
    await bot_channel.send(embed=embed)
    return
