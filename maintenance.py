
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Client, Embed
from oauth2client.service_account import ServiceAccountCredentials

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


async def maintenance(client: Client):
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    bot_notice_channel = client.get_channel(
        916608669221806100  # ビト森杯 進行bot
    )
    notice = await bot_channel.send("DB定期メンテナンス中...")

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # 各種データ取得
    tari3210 = bot_channel.guild.get_member(
        412082841829113877
    )
    # Google spreadsheetからの情報
    DB_names = await worksheet.col_values(3)
    DB_ids = await worksheet.col_values(9)

    # discordからの情報
    role_entry = bot_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = bot_channel.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    entry_names = [member.display_name for member in role_entry.members]
    reserve_names = [member.display_name for member in role_reserve.members]
    entry_ids = [member.id for member in role_entry.members]
    reserve_ids = [member.id for member in role_reserve.members]

    errors = []

    # ロール未付与(idベースで確認)
    for id in set(DB_ids) - set(entry_ids) - set(reserve_ids):
        cell_id = await worksheet.find(id)  # ロール未付与のユーザーIDを取得
        # エントリー状況を取得
        cell_status = await worksheet.cell(row=cell_id.row, col=5)
        member = bot_channel.guild.get_member(int(id))  # 該当者のmemberオブジェクトを取得

        # キャンセル待ちの場合
        if cell_status.value == "キャンセル待ち":
            await member.add_roles(role_reserve)
            errors.append(
                f"- 解決済み：キャンセル待ちロール未付与 {member.display_name} {member.id}"
            )
        if cell_status.value == "出場":
            await member.add_roles(role_entry)
            errors.append(
                f"- 解決済み：エントリーロール未付与 {member.display_name} {member.id}"
            )

    # DB未登録(idベースで確認)
    for id in set(entry_ids) + set(reserve_ids) - set(DB_ids):
        member = bot_channel.guild.get_member(int(id))  # 該当者のmemberオブジェクトを取得
        errors.append(f"- DB未登録(エントリー時刻確認) {member.display_name} {member.id}")

    # 名前が一致しているか確認
    for name in set(DB_names) - set(entry_names + reserve_names):
        cell_name = await worksheet.find(name)  # 該当者のセルを取得
        # 該当者のユーザーIDを取得
        cell_id = await worksheet.cell(row=cell_name.row, col=9)
        member = bot_channel.guild.get_member(
            int(cell_id.value)  # 該当者のmemberオブジェクトを取得
        )
        member = await member.edit(nick=name)  # ユーザー名を変更
        errors.append(f"- 解決済み：名前変更検知 {member.display_name} {member.id}")
        await bot_notice_channel.send(
            f"{member.mention}\nユーザー名の変更を検知したため、エントリー申請の際に記入した名前に変更しました。\
            \n\nユーザー名の変更はご遠慮ください。"
        )

    # 結果通知
    if bool(errors):
        embed = Embed(
            title="DBメンテナンス結果",
            description="\n".join(errors),
            color=red
        )
        await notice.reply(tari3210.mention, embed=embed)
    else:
        embed = Embed(
            title="DBメンテナンス結果",
            description="エラーはありませんでした。",
            color=green
        )
        await notice.reply(embed=embed)


async def entry_list_update(client: Client):
    bot_notice_channel = client.get_channel(
        916608669221806100  # ビト森杯 進行bot
    )
    role = bot_notice_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    dt_now = datetime.now(JST)

    entry_list = [member.display_name for member in role.members]   # エントリー名簿
    embed = Embed(
        title="参加者一覧",
        description="\n".join(entry_list),
        color=blue
    )
    embed.timestamp = dt_now

    await bot_notice_channel.send(embed=embed)
