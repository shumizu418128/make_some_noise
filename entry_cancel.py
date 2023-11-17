
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Embed, Member
from oauth2client.service_account import ServiceAccountCredentials

JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff


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


async def entry_cancel(member: Member):
    bot_channel = member.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = member.guild.get_member(
        412082841829113877
    )
    # 問い合わせスレッドを取得
    thread = await search_contact(member=member)

    # キャンセル完了通知
    embed = Embed(
        title="エントリーキャンセル",
        description="ビト森杯エントリーキャンセル完了しました。",
        color=green
    )
    embed.timestamp = datetime.now(JST)
    await thread.send(member.mention, embed=embed)

    role_check = [
        member.get_role(
            1036149651847524393),  # ビト森杯
        member.get_role(
            1172542396597289093)   # キャンセル待ち ビト森杯
    ]

    # ロール削除
    if role_check[0]:  # ビト森杯
        role = member.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        await member.remove_roles(role)
    if role_check[1]:  # キャンセル待ち ビト森杯
        role_reserve = member.guild.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
        await member.remove_roles(role_reserve)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # DBから削除
    cell_id = await worksheet.find(f'{member.id}')
    if bool(cell_id):  # DB登録あり
        for i in range(3, 10):
            await worksheet.update_cell(cell_id.row, i, '')
    else:  # DB登録なし
        await bot_channel.send(f"{tari3210.mention}\nError: DB登録なし\nキャンセル作業中止\n\n{thread.jump_url}")
        return

    # 通知
    embed = Embed(
        title="エントリーキャンセル",
        description=thread.jump_url,
        color=blue
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )
    await bot_channel.send(embed=embed)
