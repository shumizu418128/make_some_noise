
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import ButtonStyle, Client, Embed, Member
from discord.ui import Button, View
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

    await bot_channel.send(f"{member.display_name}さんがエントリーキャンセルしました。\n\n{thread.jump_url}")


async def entry_replacement(client: Client):
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    role = bot_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = bot_channel.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # キャンセル待ちへの通知
    while len(role_reserve) > 0 and len(role) < 16:  # キャンセル待ちがいて、出場枠に空きがある場合
        # キャンセル待ちの順番最初の人を取得
        cell_wait_list = await worksheet.find("キャンセル待ち", in_column=5)

        # ユーザーIDを取得
        cell_id = await worksheet.cell(row=cell_wait_list.row, col=9)
        member_replace = bot_channel.guild.get_member(int(cell_id.value))

        # 問い合わせスレッドを取得
        thread = await search_contact(member=member_replace)

        embed = Embed(
            title="繰り上げ出場通知",
            description=f"エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                \n\n出場する場合: **出場**\nキャンセルする場合: **キャンセル**\n\nとこのチャットに入力してください↓↓↓",
            color=green)
        button_call_admin = Button(
            label="ビト森杯運営に問い合わせ",
            style=ButtonStyle.primary,
            custom_id="button_call_admin",
            emoji="📩")
        view = View(timeout=None)
        view.add_item(button_call_admin)

        await thread.send(embed=embed, view=view)

        # 出場意思確認
        def check(m):
            return m.channel == thread and m.content in ["出場", "キャンセル"]
        message = await client.wait_for('message', check=check)

        # 出場する
        if message.content == "出場":
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。",
                color=green)
            await thread.send(embed=embed)  # 通知

            # ロール付け替え
            await member_replace.remove_roles(role_reserve)
            await member_replace.add_roles(role)

            # DB更新
            await worksheet.update_cell(cell_id.row, 5, "出場")
            cell_time = await worksheet.cell(row=cell_id.row, col=8)
            await worksheet.update_cell(cell_time.row, cell_time.col, cell_time.value + " 繰り上げ: " + datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))

            await bot_channel.send(f"{member_replace.display_name}さんが繰り上げ出場しました。\n\n{thread.jump_url}")
            return

        # キャンセルする
        if message.content == "キャンセル":
            await entry_cancel(member_replace)
