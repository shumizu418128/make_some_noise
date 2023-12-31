import re
from datetime import datetime, timedelta, timezone

from discord import Embed, Interaction, Member, TextStyle
from discord.ui import Modal, TextInput

from contact import contact_start, debug_log, get_worksheet, search_contact

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


class modal_entry(Modal):  # self = Modal, category = "bitomori" or "exhibition"
    def __init__(self, display_name: str, category: str):
        super().__init__(title="エントリー受付", custom_id=f"modal_entry_{category}")

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
        self.add_item(TextInput(
            label="使用するデバイス（すべて記入）",
            placeholder="使用するデバイス",
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
        await interaction.response.defer(ephemeral=True, thinking=True)

        role = interaction.guild.get_role(
            1036149651847524393  # ビト森杯
        )
        role_reserve = interaction.guild.get_role(
            1172542396597289093  # キャンセル待ち ビト森杯
        )
        role_exhibition = interaction.guild.get_role(
            1171760161778581505  # エキシビション
        )
        tari3210 = interaction.guild.get_member(
            412082841829113877
        )
        # ビト森杯エントリー済みかどうか確認
        # ビト森杯はanyでキャンセル待ちも含む
        role_check = [
            any([
                interaction.user.get_role(
                    1036149651847524393  # ビト森杯
                ),
                interaction.user.get_role(
                    1172542396597289093  # キャンセル待ち ビト森杯
                )
            ]),
            interaction.user.get_role(
                1171760161778581505  # エキシビション
            )
        ]
        # Google spreadsheet worksheet読み込み
        worksheet = await get_worksheet('エントリー名簿')

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
            await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)
            return

        # ビト森杯エントリー済み
        if role_check[0] and category == "bitomori":
            embed = Embed(
                title="エントリー済み",
                description="ビト森杯\nすでにエントリー済みです。",
                color=red
            )
            await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)
            return

        # エキシビションエントリー済み
        if role_check[1] and category == "exhibition":
            embed = Embed(
                title="エントリー済み",
                description="Online Loopstation Exhibition Battle\nすでにエントリー済みです。",
                color=red
            )
            await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)
            return

        # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
        if any([len(role.members) >= 16, len(role_reserve.members) > 0]) and category == "bitomori":
            await interaction.user.add_roles(role_reserve)
            wait = len(role_reserve.members) + 1
            embed = Embed(
                title="キャンセル待ち登録",
                description=f"参加者数が上限に達しているため、キャンセル待ちリストに登録しました。\
                \nキャンセル待ち順番: {wait}\n\n",
                color=blue
            )
            bitomori_entry_status = "キャンセル待ち"

        # ビト森杯エントリー受付完了通知（キャンセル待ちなしで、正常にエントリー完了）
        elif category == "bitomori":
            await interaction.user.add_roles(role)
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。\
                    ビト森杯ご参加ありがとうございます。\n\n",
                color=green
            )
            bitomori_entry_status = "出場"

        # エキシビションエントリー受付完了通知
        elif category == "exhibition":
            await interaction.user.add_roles(role_exhibition)
            embed = Embed(
                title="エントリー完了",
                description="エントリー受付完了しました。\
                    Online Loopstation Exhibition Battleご参加ありがとうございます。\n\n",
                color=green
            )
            exhibition_entry_status = "参加"

        embed.set_footer(text=f"Make Some Noise! 開発者: {tari3210.display_name}", icon_url=tari3210.avatar.url)

        submission = f"受付内容\n- `名前:` {name}\
            \n- `よみがな:` {read}\n- `デバイス:` {device}\n- `備考:` {note}\
            \n\n※後ほど、{name}さん専用お問い合わせチャンネルを作成します。"
        embed.description += submission
        await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)

        # ニックネームを更新
        await interaction.user.edit(nick=name)

        # DB新規登録
        # エントリー数を更新
        num_entries = await worksheet.cell(row=3, col=1)
        num_entries.value = int(num_entries.value) + 1
        await worksheet.update_cell(row=3, col=1, value=str(num_entries.value))

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

        # memberインスタンスを再取得 (roleを更新するため)
        member = interaction.guild.get_member(interaction.user.id)

        # 問い合わせへリダイレクト
        await contact_start(client=interaction.client, member=member, entry_redirect=True)
        return


async def entry_2nd(interaction: Interaction, category: str):
    # button_entryにおいてdefer使用済み

    role = interaction.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    role_exhibition = interaction.guild.get_role(
        1171760161778581505  # エキシビション
    )
    bitomori_entry_status = ""

    # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
    if any([len(role.members) >= 16, len(role_reserve.members) > 0]) and category == "bitomori":
        await interaction.user.add_roles(role_reserve)
        wait = len(role_reserve.members) + 1
        embed = Embed(
            title="キャンセル待ち登録",
            description=f"参加者数が上限に達しているため、キャンセル待ちリストに登録しました。\
                \nキャンセル待ち順番: {wait}\
                \n\n※Online Loopstation Exhibition Battleにエントリーした際の情報をそのまま登録しました。\
                \nエントリー情報が反映されるまで、約20秒かかります。",
            color=blue
        )
        bitomori_entry_status = "キャンセル待ち"

    # ビト森杯エントリー受付完了通知（キャンセル待ちなしで、正常にエントリー完了）
    elif category == "bitomori":
        await interaction.user.add_roles(role)
        embed = Embed(
            title="エントリー完了",
            description="エントリー受付完了しました。ビト森杯ご参加ありがとうございます。\
                \n\n※Online Loopstation Exhibition Battleにエントリーした際の情報をそのまま登録しました。\
                \nエントリー情報が反映されるまで、約20秒かかります。",
            color=green
        )
        bitomori_entry_status = "出場"

    # エキシビションエントリー受付完了通知
    elif category == "exhibition":
        await interaction.user.add_roles(role_exhibition)
        embed = Embed(
            title="エントリー完了",
            description="エントリー受付完了しました。\
                Online Loopstation Exhibition Battle ご参加ありがとうございます。\
                \n\n※ビト森杯にエントリーした際の情報をそのまま登録しました。\
                \nエントリー情報が反映されるまで、約10秒かかります。",
            color=green
        )
    await interaction.followup.send(interaction.user.mention, embed=embed, ephemeral=True)

    # bot用チャットへ通知
    await debug_log(
        function_name="entry_2nd",
        description=f"エントリー完了 {category}",
        color=blue,
        member=interaction.user
    )

    # DB登録処理
    worksheet = await get_worksheet('エントリー名簿')
    cell_id = await worksheet.find(f'{interaction.user.id}')

    # OLEBへのエントリーなら、DBに "参加" と追記するだけ
    if category == "exhibition":
        await worksheet.update_cell(cell_id.row, 6, "参加")

        # 一応受付時刻は更新する
        await worksheet.update_cell(cell_id.row, 9, str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")))
        return

    # DB新規登録
    # エントリー数を更新
    num_entries = await worksheet.cell(row=3, col=1)
    num_entries.value = int(num_entries.value) + 1
    await worksheet.update_cell(row=3, col=1, value=str(num_entries.value))

    # ビト森杯へのエントリーなら、一旦新規行に登録した後、もとの行を削除する
    # もとの行のセルを取得
    cell_name = await worksheet.cell(cell_id.row, 3)
    cell_read = await worksheet.cell(cell_id.row, 4)
    cell_device = await worksheet.cell(cell_id.row, 7)
    cell_note = await worksheet.cell(cell_id.row, 8)
    cell_replace_deadline = await worksheet.cell(cell_id.row, 11)

    # もとの行の内容を取得
    name = cell_name.value
    read = cell_read.value
    device = cell_device.value
    note = cell_note.value
    replace_deadline = cell_replace_deadline.value

    # エントリー情報を書き込み
    row = int(num_entries.value) + 1
    values = [
        name,
        read,
        bitomori_entry_status,
        "参加",  # OLEB参加状況
        device,
        note,
        str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")),
        str(interaction.user.id),
        replace_deadline
    ]
    for col, value in zip(range(3, 12), values):
        await worksheet.update_cell(row=row, col=col, value=value)

    # もとの行を削除
    for col, value in zip(range(3, 12), values):
        await worksheet.update_cell(row=cell_id.row, col=col, value="")
    return


async def entry_cancel(member: Member, category: str):
    role = member.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = member.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    role_exhibition = member.guild.get_role(
        1171760161778581505  # エキシビション
    )
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
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # 問い合わせスレッドを取得
    thread = await search_contact(member=member)

    # キャンセル完了通知
    embed = Embed(
        title="エントリーキャンセル",
        color=green
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )

    # キャンセル完了通知の内容を設定
    if category == "bitomori":
        embed.description = "ビト森杯エントリーをキャンセルしました。"
    elif category == "exhibition":
        embed.description = "Online Loopstation Exhibition Battleエントリーをキャンセルしました。"

    await thread.send(member.mention, embed=embed)

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
        # すべてのロールを持っていない場合
        if any(role_check) is False:
            for i in range(3, 12):
                await worksheet.update_cell(cell_id.row, i, '')

        # bot用チャットへ通知
        await debug_log(
            function_name="entry_cancel",
            description=f"エントリーキャンセル {category}",
            color=yellow,
            member=member
        )
    # DB登録なし
    else:

        # bot用チャットへ通知
        await debug_log(
            function_name="entry_cancel",
            description=f"Error: エントリーキャンセル作業中止 DB登録なし {category} ",
            color=red,
            member=member
        )
        return
