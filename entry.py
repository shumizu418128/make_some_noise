import re
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Embed, Interaction, TextStyle
from discord.ui import Modal, TextInput
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
                label="あなたの名前",
                placeholder="名前",
                default=display_name
            )
        )
        self.add_item(
            TextInput(
                label="あなたの名前の「よみがな」",
                placeholder="よみがな"
            )
        )
        self.add_item(
            TextInput(
                label="使用するデバイス（すべて記入）",
                placeholder="使用するデバイス",
                style=TextStyle.long
            )
        )
        self.add_item(
            TextInput(
                label="備考（任意回答）",
                placeholder="連絡事項など",
                style=TextStyle.long,
                required=False
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
        if note == "":  # 備考が空欄の場合
            note = "なし"  # なしと記載

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
