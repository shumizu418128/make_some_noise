import re
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import ButtonStyle, Client, Embed, Interaction, Member, TextStyle
from discord.ui import Button, Modal, TextInput, View
from oauth2client.service_account import ServiceAccountCredentials

from contact import contact_start, search_contact

re_hiragana = re.compile(r'^[ぁ-ゞ　 ー]+$')
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


class modal_entry(Modal):
    def __init__(self, display_name):  # self = Modal
        super().__init__(title="エントリー受付", custom_id="modal_entry")

        self.add_item(
            TextInput(
                label="名前",
                placeholder="あなたの名前",
                default=display_name
            )
        )
        self.add_item(
            TextInput(
                label="よみがな",
                placeholder="あなたの名前の「よみがな」"
            )
        )
        self.add_item(
            TextInput(
                label="利用デバイス",
                placeholder="大会で利用するデバイス",
                style=TextStyle.long
            )
        )
        self.add_item(
            TextInput(
                label="備考",
                style=TextStyle.long, required=False
            )
        )

    # モーダル提出後の処理
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        # 入力内容を取得
        name = self.children[0].value
        read = self.children[1].value
        device = self.children[2].value
        note = self.children[3].value

        # よみがなのひらがな判定
        if not re_hiragana.fullmatch(read):
            embed = Embed(
                title="Error",
                description=f"登録できませんでした。\nよみがなは、**「ひらがな・伸ばし棒** `ー` **のみ」**で入力してください\
                    \n\n入力したよみがな：{read}",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ビト森杯エントリー済みかどうか確認
        role_check = [
            interaction.user.get_role(
                1036149651847524393  # ビト森杯
            ),
            interaction.user.get_role(
                1172542396597289093  # キャンセル待ち ビト森杯
            )
        ]
        if role_check[0]:  # ビト森杯エントリー済み
            embed = Embed(
                title="エントリー済み",
                description="既にエントリー済みです。",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        if role_check[1]:  # ビト森杯キャンセル待ち登録済み
            embed = Embed(
                title="キャンセル待ち登録済み",
                description="既にキャンセル待ち登録済みです。",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        role = interaction.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        role_reserve = interaction.guild.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )

        # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
        if len(role.members) >= 16 or len(role_reserve.members) > 0:
            await interaction.user.add_roles(role_reserve)
            embed = Embed(
                title="キャンセル待ち登録",
                description="エントリー数が上限に達しているため、キャンセル待ちリストに登録しました。",
                color=blue
            )
            entry_status = "キャンセル待ち"

        # エントリー受付
        else:
            await interaction.user.add_roles(role)
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。",
                color=green
            )
            entry_status = "出場"

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Google spreadsheet worksheet読み込み
        gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
        agc = await gc.authorize()
        # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
        workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
        worksheet = await workbook.worksheet('エントリー名簿')

        # エントリー数を更新
        num_entries = await worksheet.cell(row=3, col=1)
        num_entries.value = int(num_entries.value) + 1
        await worksheet.update_cell(row=3, col=1, value=num_entries.value)

        # エントリー情報を書き込み
        row = int(num_entries.value) + 1
        values = [
            name,
            read,
            entry_status,
            device,
            note,
            str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")),
            str(interaction.user.id)
        ]
        for col, value in zip(range(3, 10), values):
            await worksheet.update_cell(row=row, col=col, value=value)

        # ニックネームを更新
        await interaction.user.edit(nick=name)

        await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


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
