from discord import ButtonStyle, File, SelectOption
from discord.ui import Button, Select, View

# NOTE: ビト森杯運営機能搭載ファイル

# trueになっているボタンを表示 (falseは非表示)


class BitomoriInfoSelect(Select):
    def __init__(self):
        options = [
            SelectOption(
                label="開催日・配信",
                description="ビト森杯・Online Loopstation Exhibition Battleの開催日時と配信",
                value="title",
                emoji="📅"
            ),
            SelectOption(
                label="賞金",
                description="ビト森杯の賞金",
                value="prize",
                emoji="💰"
            ),
            SelectOption(
                label="ビト森杯ルール",
                description="ビト森杯のルール・参加条件",
                value="rule_bitomori",
                emoji="📜"
            ),
            SelectOption(
                label="OLEBルール",
                description="Online Loopstation Exhibition Battleのルール・参加条件",
                value="rule_exhibition",
                emoji="📜"
            ),
            SelectOption(
                label="ビト森杯2ndデバイスルール",
                description="ビト森杯の2ndデバイスルール (Online Loopstation Exhibition Battleは無制限)",
                value="2nd_device",
                emoji="📜"
            ),
            SelectOption(
                label="参加方法",
                description="ビト森杯・Online Loopstation Exhibition Battleの参加手続き方法",
                value="entry",
                emoji="📝"
            ),
            SelectOption(
                label="エントリー受付期間",
                description="ビト森杯・Online Loopstation Exhibition Battleのエントリー受付開始日・締め切り日",
                value="entry_period",
                emoji="📅"
            ),
            SelectOption(
                label="ビト森杯タイムスケジュール",
                description="ビト森杯当日のタイムスケジュール (Online Loopstation Exhibition Battleは後日発表)",
                value="time_schedule",
                emoji="📅"
            ),
            SelectOption(
                label="ビト森杯キャンセル待ち",
                description="ビト森杯には人数制限があります キャンセル待ち登録を行った方はこちらをご確認ください",
                value="replace",
                emoji="📝"
            ),
        ]
        super().__init__(placeholder="選択してください", options=options)

    async def callback(self, interaction):
        value = interaction.data["values"][0]
        await interaction.response.send_message(
            file=File(f"{value}.jpg"),
            ephemeral=True
        )
        return


async def get_view(
    contact: bool = False,
    call_admin: bool = False,
    submission_content: bool = False,
    cancel: bool = False,
    entry_bitomori: bool = False,
    entry_exhibition: bool = False,
    entry: bool = False,
    replace: bool = False,
    admin: bool = False,
    info: bool = False
):
    view = View(timeout=None)

    button_contact = Button(
        label="お問い合わせチャンネル作成",
        style=ButtonStyle.primary,
        custom_id="button_contact",
        emoji="📝"
    )
    button_call_admin = Button(
        label="運営に問い合わせ",
        style=ButtonStyle.primary,
        custom_id="button_call_admin",
        emoji="📩"
    )
    button_submission_content = Button(
        label="エントリー状況照会",
        style=ButtonStyle.gray,
        custom_id="button_submission_content",
        emoji="🔍"
    )
    button_cancel = Button(
        label="エントリーキャンセル",
        style=ButtonStyle.red,
        custom_id="button_cancel",
        emoji="😭"
    )
    button_entry_bitomori = Button(
        style=ButtonStyle.green,
        label="ビト森杯エントリー",
        custom_id="button_entry_bitomori",
        emoji="🏆"
    )
    button_entry_exhibition = Button(
        style=ButtonStyle.green,
        label="OLEBエントリー",
        custom_id="button_entry_exhibition",
        emoji="⚔️"
    )
    # 問い合わせスレッド作成
    if contact:
        view.add_item(button_contact)

    # 運営呼び出し
    if call_admin:
        view.add_item(button_call_admin)

    # エントリー状況照会
    if submission_content:
        view.add_item(button_submission_content)

    # キャンセル
    if cancel:
        view.add_item(button_cancel)

    # ビト森杯エントリー
    if entry_bitomori or entry:
        view.add_item(button_entry_bitomori)

    # OLEBエントリー
    if entry_exhibition or entry:
        view.add_item(button_entry_exhibition)

    # entry = entry_bitomori and entry_exhibition

    # 繰り上げ出場
    button_accept_replace = Button(
        style=ButtonStyle.green,
        label="ビト森杯に出場する",
        custom_id="button_accept_replace",
        emoji="✅"
    )
    if replace:
        view.add_item(button_accept_replace)
        view.add_item(button_cancel)
        view.add_item(button_call_admin)

    # 運営用ボタン
    button_admin_entry_bitomori = Button(
        style=ButtonStyle.green,
        label="ビト森杯エントリー",
        custom_id="button_admin_entry_bitomori",
        emoji="👑"
    )
    button_admin_entry_exhibition = Button(
        style=ButtonStyle.green,
        label="OLEBエントリー",
        custom_id="button_admin_entry_exhibition",
        emoji="👑"
    )
    button_admin_cancel = Button(
        style=ButtonStyle.red,
        label="キャンセル",
        custom_id="button_admin_cancel",
        emoji="👑"
    )
    button_admin_create_thread = Button(
        style=ButtonStyle.green,
        label="問い合わせチャンネル作成",
        custom_id="button_admin_create_thread",
        emoji="👑"
    )
    button_admin_submission_content = Button(
        style=ButtonStyle.gray,
        label="エントリー状況照会",
        custom_id="button_admin_submission_content",
        emoji="👑"
    )
    if admin:
        view.add_item(button_admin_entry_bitomori)
        view.add_item(button_admin_entry_exhibition)
        view.add_item(button_admin_cancel)
        view.add_item(button_admin_create_thread)
        view.add_item(button_admin_submission_content)

    if info:
        view.add_item(BitomoriInfoSelect())

    return view
