from discord import ButtonStyle
from discord.ui import Button, View


# NOTE: ビト森杯運営機能搭載ファイル
async def get_view(
    contact: bool = False,
    call_admin: bool = False,
    submission_content: bool = False,
    cancel: bool = False,
    entry: bool = False,
    replace: bool = False
):
    button_contact = Button(
        label="お問い合わせチャンネル作成",
        style=ButtonStyle.primary,
        custom_id="button_contact",
        emoji="📝"
    )
    button_call_admin = Button(
        label="ビト森杯運営に問い合わせ",
        style=ButtonStyle.primary,
        custom_id="button_call_admin",
        emoji="📩"
    )
    button_cancel = Button(
        label="エントリーキャンセル",
        style=ButtonStyle.red,
        custom_id="button_cancel",
        emoji="❌"
    )
    button_submission_content = Button(
        label="エントリー状況照会",
        style=ButtonStyle.gray,
        custom_id="button_submission_content",
        emoji="🔍"
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
        emoji="🆚"
    )
    view = View(timeout=None)

    # 問い合わせスレッド作成
    if contact:
        view.add_item(button_contact)

    # 運営呼び出し
    if call_admin:
        view.add_item(button_call_admin)

    # エントリー状況照会
    if submission_content:
        view.add_item(button_submission_content)

    # エントリー
    if entry:
        view.add_item(button_entry_bitomori)
        view.add_item(button_entry_exhibition)

    # キャンセル
    if cancel:
        view.add_item(button_cancel)

    # 繰り上げ出場
    button_accept_replace = Button(
        style=ButtonStyle.green,
        label="ビト森杯に出場する",
        custom_id="button_accept_replace",
        emoji="✅"
    )
    button_cancel = Button(
        label="エントリーキャンセル",
        style=ButtonStyle.red,
        custom_id="button_cancel",
        emoji="❌"
    )
    button_call_admin = Button(
        label="ビト森杯運営に問い合わせ",
        style=ButtonStyle.primary,
        custom_id="button_call_admin",
        emoji="📩"
    )
    if replace:
        view.add_item(button_accept_replace)
        view.add_item(button_cancel)
        view.add_item(button_call_admin)
    return view
