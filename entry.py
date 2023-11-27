import re
from datetime import datetime, timedelta, timezone

import gspread_asyncio
from discord import Embed, Interaction, Member, TextStyle
from discord.ui import Modal, TextInput
from oauth2client.service_account import ServiceAccountCredentials

from contact import contact_start, search_contact

# NOTE: ビト森杯運営機能搭載ファイル
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


class modal_entry(Modal):  # self = Modal, category = "bitomori" or "exhibition"
    def __init__(self, display_name: str, category: str):
        super().__init__(title="エントリー受付", custom_id=f"modal_entry_{category}")

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

    # TODO: 動作テスト
    # モーダル提出後の処理
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        role = interaction.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        role_reserve = interaction.guild.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
        role_exhibition = interaction.guild.get_role(
            1171760161778581505  # エキシビション
        )
        bot_channel = interaction.guild.get_channel(
            897784178958008322  # bot用チャット
        )
        # ビト森杯エントリー済みかどうか確認
        role_check = [
            interaction.user.get_role(
                1036149651847524393  # ビト森杯
            ),
            interaction.user.get_role(
                1172542396597289093  # キャンセル待ち ビト森杯
            ),
            interaction.user.get_role(
                1171760161778581505  # エキシビション
            )
        ]
        category = self.custom_id.split("_")[2]  # "bitomori" or "exhibition"

        # 入力内容を取得
        name = self.children[0].value
        read = self.children[1].value
        device = self.children[2].value
        note = self.children[3].value
        if note == "":  # 備考が空欄の場合
            note = "なし"  # なしと記載

        bitomori_entry_status = ""
        exhibition_entry_status = ""

        # よみがなのひらがな判定
        if not re_hiragana.fullmatch(read):
            embed = Embed(
                title="❌ Error ❌",
                description=f"エントリーに失敗しました。\nよみがなは、**「ひらがな・伸ばし棒** `ー` **のみ」** で入力してください\
                    \n\n入力したよみがな：{read}",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ビト森杯エントリー済み
        if role_check[0] and category == "bitomori":
            embed = Embed(
                title="エントリー済み",
                description="ビト森杯\nすでにエントリー済みです。",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # ビト森杯キャンセル待ち登録済み
        if role_check[1] and category == "bitomori":
            embed = Embed(
                title="キャンセル待ち登録済み",
                description="すでにビト森杯キャンセル待ち登録済みです。",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # エキシビションエントリー済み
        if role_check[2] and category == "exhibition":
            embed = Embed(
                title="エントリー済み",
                description="Online Loopstation Exhibition Battle\nすでにエントリー済みです。",
                color=red
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
        if any([len(role.members) >= 16, len(role_reserve.members) > 0]) and category == "bitomori":
            await interaction.user.add_roles(role_reserve)
            embed = Embed(
                title="キャンセル待ち登録",
                description="参加者数が上限に達しているため、キャンセル待ちリストに登録しました。\n\n",
                color=blue
            )
            bitomori_entry_status = "キャンセル待ち"

        # ビト森杯エントリー受付完了通知
        elif category == "bitomori":
            await interaction.user.add_roles(role)
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。\n\n",
                color=green
            )
            bitomori_entry_status = "出場"

        # エキシビションエントリー受付完了通知
        elif category == "exhibition":
            await interaction.user.add_roles(role_exhibition)
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。\n\n",
                color=green
            )
            exhibition_entry_status = "参加"

        submission = f"受付内容\n- 名前: {name}\
            \n- よみがな: {read}\n- デバイス: {device}\n- 備考: {note}"
        embed.description += submission
        await interaction.followup.send(embed=embed, ephemeral=True)

        # 一応bot_channelにも通知
        embed = Embed(
            title=f"modal_entry_{category}",
            description=submission,
            color=blue
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.avatar.url
        )
        await bot_channel.send(f"{interaction.user.id}", embed=embed)

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
            bitomori_entry_status,
            exhibition_entry_status,
            device,
            note,
            str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")),
            str(interaction.user.id)
        ]
        for col, value in zip(range(3, 11), values):
            await worksheet.update_cell(row=row, col=col, value=value)

        # ニックネームを更新
        await interaction.user.edit(nick=name)
        await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


# TODO: 動作テスト
# TODO: OLEB実装
async def entry_cancel(member: Member, category: str):
    bot_channel = member.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = member.guild.get_member(
        412082841829113877
    )
    role = member.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = member.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    role_exhibition = member.guild.get_role(
        1171760161778581505  # エキシビション
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
            1036149651847524393  # ビト森杯
        ),
        member.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        ),
        member.get_role(
            1171760161778581505  # エキシビション
        )
    ]

    # ロール削除
    if role_check[0] and category == "bitomori":  # ビト森杯
        await member.remove_roles(role)

    if role_check[1] and category == "bitomori":  # キャンセル待ち ビト森杯
        await member.remove_roles(role_reserve)

    if role_check[2] and category == "exhibition":  # エキシビション
        await member.remove_roles(role_exhibition)

    # Google spreadsheet worksheet読み込み
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    # https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0
    workbook = await agc.open_by_key('1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw')
    worksheet = await workbook.worksheet('エントリー名簿')

    # DBのセルを特定
    cell_id = await worksheet.find(f'{member.id}')

    if bool(cell_id):  # DB登録あり
        for i in range(3, 12):
            await worksheet.update_cell(cell_id.row, i, '')
    else:  # DB登録なし
        await bot_channel.send(f"{tari3210.mention}\nError: DB登録なし\nキャンセル作業中止\n\n{thread.jump_url}")
        return

    # 通知
    embed = Embed(
        title=f"キャンセル実行 {category}",
        description=thread.jump_url,
        color=blue
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )
    await bot_channel.send(embed=embed)
