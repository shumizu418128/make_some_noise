import re
from datetime import timedelta, timezone

from discord import Interaction, Member, TextStyle
from discord.ui import Modal, TextInput

import database

# NOTE: ビト森杯運営機能搭載ファイル
re_hiragana = re.compile(r'^[ぁ-ゞ　 ー]+$')
JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff

"""
ここでは原則バックグラウンドの処理を行う
エントリー処理はprocess_entry関数で行う
modal提出の対応はon_interactionにて行う
フロントエンドの処理はcallback.pyにて行う
"""


class Modal_entry(Modal):  # self = Modal, category = soloA, soloB, loop
    def __init__(self, display_name: str, category: str):
        super().__init__(
            title=f"エントリー受付 {category}", custom_id=f"modal_entry_{category}")

        self.add_item(TextInput(
            label="あなたの名前",
            placeholder="名前",
            default=display_name,
            custom_id="name"
        ))
        self.add_item(TextInput(
            label="あなたの名前の「よみがな」（ひらがな）",
            placeholder="よみがな（ひらがな）",
            custom_id="read"
        ))
        if category == "loop":
            self.add_item(TextInput(
                label="使用するLoopstationデバイス（すべて記入）",
                placeholder="Loopデバイス",
                style=TextStyle.long,
                custom_id="device"
            ))
        self.add_item(TextInput(
            label="備考（任意回答）",
            placeholder="連絡事項など",
            style=TextStyle.long,
            required=False,
            custom_id="note"
        ))

    # モーダル提出後の処理
    async def on_submit(self, interaction: Interaction):
        # TODO: なんかやらないと怒られるので適当に処理
        # エントリー処理はprocess_entry関数で行う
        # modal提出の対応はon_interactionにて行う
        return


# エントリー処理
async def process_entry(member: Member, category: str, input_contents: dict):
    # エントリーした部門のidを取得
    role_ids = {
        "loop": (database.ROLE_LOOP, database.ROLE_LOOP_RESERVE),
        "soloA": (database.ROLE_SOLO_A, database.ROLE_SOLO_A_RESERVE),
        "soloB": (database.ROLE_SOLO_B, database.ROLE_SOLO_B_RESERVE),
    }
    # categoryに対応するIDを取得
    # 正しく取得できていない場合はValueErrorが発生する
    id, id_reserve = role_ids.get(category)

    #########################
    # エントリー失敗時のエラー処理
    #########################

    # ビト森杯エントリー済みかどうか確認
    user_role_statuses = any([
        member.get_role(id),
        member.get_role(id_reserve)
    ])
    if user_role_statuses:
        return "Error: エントリー済み"

    # よみがなのひらがな判定
    if not re_hiragana.fullmatch(input_contents["read"]):
        return "Error: よみがなエラー"

    #########################
    # 以下エントリー処理
    #########################

    # IDからroleを取得
    role = member.guild.get_role(id)
    role_reserve = member.guild.get_role(id_reserve)

    # 備考が空欄の場合、なしと記載
    if input_contents["note"] == "":
        input_contents["note"] = "なし"

    # TODO: スプシを作る（3部門の記録をどう管理するか）
    # TODO: ここから下はまだ取り掛かってない input_contentsがない場合を考える
    # Google spreadsheet worksheet読み込み
    worksheet = await database.get_worksheet('エントリー名簿')

    # DB新規登録
    # エントリー数を更新
    num_entries = await worksheet.cell(row=3, col=1)
    num_entries.value = int(num_entries.value) + 1
    await worksheet.update_cell(row=3, col=1, value=str(num_entries.value))

    # ニックネームを更新
    await member.edit(nick=input_contents["name"])

    if any([len(role.members) >= 16, len(role_reserve.members) > 0]):
        await member.add_roles(role_reserve)
        return "Approved: キャンセル待ち"

    else:
        await member.add_roles(role)
        return "Approved: エントリー完了"


async def entry_cancel(member: Member, category: str):
    # ビト森杯
    role = member.guild.get_role(database.ROLE_LOOP)

    # キャンセル待ち ビト森杯
    role_reserve = member.guild.get_role(database.ROLE_LOOP_RESERVE)

    # エキシビション
    role_exhibition = member.guild.get_role(database.ROLE_OLEB)

    role_check = [
        member.get_role(database.ROLE_LOOP),
        member.get_role(database.ROLE_LOOP_RESERVE),
        member.get_role(database.ROLE_OLEB)
    ]
    # Google spreadsheet worksheet読み込み
    worksheet = await database.get_worksheet('エントリー名簿')

    # DBのセルを取得
    cell_id = await worksheet.find(f'{member.id}')

    # ロール削除
    if role_check[0] and category == "bitomori":  # ビト森杯
        await member.remove_roles(role)
    if role_check[1] and category == "bitomori":  # キャンセル待ち ビト森杯
        await member.remove_roles(role_reserve)
    if role_check[2] and category == "exhibition":  # エキシビション
        await member.remove_roles(role_exhibition)

    # DB登録あり
    if bool(cell_id):

        # ビト森杯出場可否・OLEB参加状況を削除
        if category == "bitomori":
            await worksheet.update_cell(cell_id.row, 5, '')

            # キャンセル待ち繰り上げ手続き中の場合、その情報も削除
            await worksheet.update_cell(cell_id.row, 11, '')

        if category == "exhibition":
            await worksheet.update_cell(cell_id.row, 6, '')

        # 両方のエントリーをキャンセルした場合、DBの行を削除
        # memberインスタンスを再取得 (roleを更新するため)
        member = member.guild.get_member(member.id)

        # role_checkを再取得
        role_check = [
            member.get_role(database.ROLE_LOOP),
            member.get_role(database.ROLE_LOOP_RESERVE),
            member.get_role(database.ROLE_OLEB)
        ]
        # すべてのロールを持っていない場合、DBの行を削除
        if any(role_check) is False:
            for i in range(3, 12):
                await worksheet.update_cell(cell_id.row, i, '')
        return

    # DB登録なし
    else:
        return "Error: DB登録なし"
