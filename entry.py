import re
from datetime import timedelta, timezone

from discord import Embed, Interaction, Member, TextStyle
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

        tari3210 = interaction.guild.get_member(database.TARI3210)
        bot_channel = interaction.guild.get_channel(database.CHANNEL_BOT)

        # エントリーした部門のidを取得
        role_ids = {
            "loop": (database.ROLE_LOOP, database.ROLE_LOOP_RESERVE),
            "soloA": (database.ROLE_SOLO_A, database.ROLE_SOLO_A_RESERVE),
            "soloB": (database.ROLE_SOLO_B, database.ROLE_SOLO_B_RESERVE),
        }
        category = interaction.custom_id.split("_")[-1]
        id, id_reserve = role_ids.get(category)

        role = interaction.guild.get_role(id)
        role_reserve = interaction.guild.get_role(id_reserve)

        # process_entryの処理完了を待って、正しく処理されたか確認
        # roleの追加を確認するため、member_updateイベントを待つ
        def check(before, after):
            role_check_before = any([
                before.get_role(id),
                before.get_role(id_reserve)
            ])
            role_check_after = any([
                after.get_role(id),
                after.get_role(id_reserve)
            ])
            return after.id == interaction.user.id and role_check_after > role_check_before

        try:
            _, after = await interaction.client.wait_for("member_update", check=check, timeout=180)

        # 3分経ってもエントリーが完了しない場合一応報告
        except TimeoutError:
            embed = Embed(
                title="Modal_entry on_submit",
                description="Error: member_updateキャッチ失敗\n※Modal提出を拒否している場合、異常なし",
                color=red
            )
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            await bot_channel.send(tari3210.mention, embed=embed)
            return

        # エントリーした人の情報を取得
        # 提出者の名前、id
        member_name = after.display_name
        member_id = interaction.user.id

        for role_member in role.members + role_reserve.members:

            # 名前がすでに登録済みで、かつidが違う場合はエラーを出力
            if role_member.id != member_id and role_member.display_name == member_name:

                embed = Embed(
                    title="Modal_entry on_submit",
                    description=f"Error: 同じ名前のエントリーを確認\n\n提出者: {after.mention}\n被った人: {role_member.mention}",
                    color=red
                )
                await bot_channel.send(tari3210.mention, embed=embed)
        return


# エントリー処理
async def process_entry(member: Member, category: str, input_contents: dict):
    """
    Args:
        `member (Member):` エントリーするメンバー
        `category (str):` エントリーする部門
        `input_contents (dict):` 提出内容
        >>> input_contents = {
            "name": "名前",
            "read": "よみがな",
            "device": "Loopstationデバイス", # loop部門のみ
            "note": "備考"
        }

    Returns:
        `color, title, description (dict[str]):` 処理結果
    """
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
        return {"color": red, "title": "❌Error❌", "description": "すでにエントリー済みです"}

    # よみがなのひらがな判定
    if not re_hiragana.fullmatch(input_contents["read"]):
        return {"color": red, "title": "❌Error❌", "description": "よみがなは ひらがな・伸ばし棒`ー`・スペース のみで入力してください"}

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

    # エントリー数が16人以上の場合 or キャンセル待ちにすでに人がいる場合、キャンセル待ちにする
    if any([len(role.members) >= 16, len(role_reserve.members) > 0]):

        # キャンセル待ちの人数を取得
        count = len(role_reserve.members) + 1

        await member.add_roles(role_reserve)
        return {"color": green, "title": "キャンセル待ち登録完了", "description": f"キャンセル待ち {count}番目\n🙇ご参加ありがとうございます！🙇"}

    else:
        await member.add_roles(role)
        return {"color": green, "title": "エントリー完了", "description": "🙇ご参加ありがとうございます！🙇"}


# TODO; 第4回ビト森杯実装
async def entry_cancel(member: Member, category: str):
    """
    Args:
        `member (Member):` キャンセルするメンバー
        `category (str):` キャンセルする部門

    Returns:
        `None or "Error"`
    """
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
