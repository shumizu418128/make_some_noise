from datetime import datetime, timedelta, timezone

from discord import Embed, Interaction

from contact import contact_start, get_worksheet, search_contact
from entry import entry_cancel, modal_entry

# NOTE: ビト森杯運営機能搭載ファイル
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


# TODO: 動作テスト
# 両カテゴリーのエントリーを受け付ける
async def button_entry(interaction: Interaction):
    # エントリー開始時刻を定義
    dt_now = datetime.now(JST)
    dt_entry_start = datetime(
        year=2024,
        month=1,
        day=6,
        tzinfo=JST
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
    # エントリーカテゴリー取得
    category = interaction.data["custom_id"].replace("button_entry_", "")

    # localeを取得
    locale = str(interaction.locale)

    # 問い合わせスレッドがある場合はそこからlocaleを取得
    thread = await search_contact(member=interaction.user)
    if bool(thread):
        locale = thread.name.split("_")[1]

    # エントリー開始時刻確認
    if dt_now < dt_entry_start:
        await interaction.response.send_message(
            "エントリー受付開始は1月6日です。",
            ephemeral=True)
        return

    # ビト森杯エントリー済み
    if role_check[0] and category == "bitomori":
        embed = Embed(
            title="エントリー済み",
            description="ビト森杯\nすでにエントリー済みです。",
            color=red
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # エキシビションエントリー済み
    if role_check[1] and category == "exhibition":
        embed = Embed(
            title="エントリー済み",
            description="Online Loopstation Exhibition Battle\nすでにエントリー済みです。",
            color=red
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # 日本からのビト森杯エントリー
    if locale == "ja" and category == "bitomori":
        await interaction.response.send_modal(modal_entry(interaction.user.display_name, "bitomori"))
        return

    # 日本からのOLEBエントリー
    if locale == "ja" and category == "exhibition":
        await interaction.response.send_modal(modal_entry(interaction.user.display_name, "exhibition"))
        return

    # 以下モーダル送信しないのでdeferをかける
    await interaction.response.defer(ephemeral=True)

    # 海外からのエントリー
    thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))

    # 各種言語の文言
    available_langs = [
        "ko", "zh-TW", "zh-CN",
        "en-US", "en-GB", "es-ES", "pt-BR"
    ]

    # localeが利用可能言語に含まれていない場合は英語にする
    if locale not in available_langs:
        locale = "en-US"
    langs = {
        "en-US": f"Error: please contact us via {thread.mention}",
        "en-GB": f"Error: please contact us via {thread.mention}",
        "zh-TW": f"錯誤：請點一下 {thread.mention} 聯係我們",
        "zh-CN": f"错误：请点击 {thread.mention} 联系我们 ※此服务器仅以日英交流",
        "ko": f"문의는 {thread.mention} 로 보내주세요",
        "es-ES": f"Error: por favor contáctenos a través de {thread.mention}",
        "pt-BR": f"Erro: entre em contato conosco através de {thread.mention}"
    }
    description = langs[locale] + \
        f"\nお手数ですが {thread.mention} までお問い合わせください。"

    # 一旦エラー文言を送信
    embed = Embed(
        title="contact required: access from overseas",
        description=description,
        color=red
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

    # 問い合わせスレッドにリダイレクト
    await contact_start(client=interaction.client, member=interaction.user, entry_redirect=True)


async def button_contact(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)

    # 問い合わせスレッドを取得or作成
    thread = await search_contact(member=interaction.user, create=True, locale=str(interaction.locale))
    embed = Embed(
        title="お問い合わせチャンネル作成",
        description=f"{thread.jump_url} までお問い合わせください。",
        color=0x00bfff
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

    # 問い合わせ対応開始
    await contact_start(client=interaction.client, member=interaction.user)


# TODO: 動作テスト
async def button_call_admin(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    contact = interaction.client.get_channel(
        1035964918198960128  # 問い合わせ
    )
    admin = interaction.user.get_role(
        904368977092964352  # ビト森杯運営
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = interaction.guild.get_member(
        412082841829113877
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
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
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # しゃべってよし
    await contact.set_permissions(interaction.user, send_messages_in_threads=True)

    # 要件を書くよう案内
    embed = Embed(
        title="このチャンネルにご用件をご記入ください",
        description="運営が対応します",
        color=blue
    )
    await interaction.followup.send(interaction.user.mention, embed=embed)
    await interaction.channel.send("↓↓↓ このチャットにご記入ください ↓↓↓")

    # メッセージが来たら運営へ通知
    def check(m):
        return m.channel == contact and m.author == interaction.user

    msg = await interaction.client.wait_for('message', check=check)
    await msg.reply(
        f"{admin.mention}\n{interaction.user.display_name}さんからの問い合わせ",
        mention_author=False
    )
    # ビト森杯のどちらのロールも持っている場合（異常なロール付与）
    if role_check[0] and role_check[1]:
        await bot_channel.send(f"{tari3210.mention}\nbutton_call_admin Error: 重複ロール付与\n\n{interaction.channel.jump_url}")
        return

    # 何かしらエントリーしている
    if any(role_check):

        # DBから取得
        cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索

        # DB登録あり
        if bool(cell_id):

            # ユーザーIDの行の値を取得
            cell_values = await worksheet.row_values(cell_id.row)
            name = cell_values[2]
            read = cell_values[3]
            status_bitomori = cell_values[4]
            status_exhibition = cell_values[5]
            device = cell_values[6]
            note = cell_values[7]
            time = cell_values[8]
            replace_deadline = cell_values[10]

            # エントリー情報詳細のembedを作成
            embed_entry_status = Embed(
                title="エントリー情報詳細",
                description=f"- 名前: {name}\n- 読み: {read}\n- ビト森杯出場可否: {status_bitomori}\
                    \n- OLEB参加状況: {status_exhibition}\n- デバイス: {device}\n- 備考: {note}\
                    \n- 受付時刻: {time}"
            )
            # キャンセル待ちの場合、情報を追記
            if role_check[1]:

                # キャンセル待ちの順番最初の人を取得
                cell_wait_first = await worksheet.find("キャンセル待ち", in_column=5)

                # キャンセル待ちの順番を取得
                cell_waitlist_position = cell_id.row - cell_wait_first.row + 1

                # 繰り上げ手続き中でない場合、待ち人数を表示
                if bool(replace_deadline) is False:
                    embed_entry_status.description += f"\n- キャンセル待ち {len(role_reserve)}人中 {cell_waitlist_position}番目"

                # 繰り上げ手続き中の場合、締切日を表示
                else:
                    embed_entry_status.description += "\n- 繰り上げ手続き締切: " + replace_deadline

            # ボタンを押したチャンネルへ通知
            await interaction.channel.send(embed=embed_entry_status)

        # DB登録なし
        else:
            await bot_channel.send(f"{tari3210.mention}\nbutton_call_admin Error: DB登録なし\n\n{interaction.channel.jump_url}")

    # 何もエントリーしていない
    else:

        # エントリー情報詳細のembedを作成
        embed = Embed(
            title="エントリー情報詳細",
            description=f"{interaction.user.display_name}さんはエントリーしていません。"
        )
        await interaction.channel.send(embed=embed)


# TODO: 動作テスト
async def button_cancel(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
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
    emoji = ""

    # そもそもエントリーしてる？
    # どちらのロールも持っていない場合
    if any(role_check) is False:
        embed = Embed(
            title="エントリーキャンセル",
            description=f"Error: {interaction.user.display_name}さんはエントリーしていません。",
            color=red
        )
        await interaction.followup.send(embed=embed)
        return

    # 両方にエントリーしている場合
    if all(role_check):

        # キャンセルするカテゴリーを選択
        embed = Embed(
            title="エントリーキャンセル",
            description="どちらのエントリーをキャンセルしますか？\n🏆 ビト森杯\
                \n🆚 Online Loopstation Exhibition Battle\n❌ このメッセージを削除する",
            color=yellow
        )
        notice = await interaction.followup.send(embed=embed)
        await notice.add_reaction("🏆")
        await notice.add_reaction("🆚")
        await notice.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and reaction.emoji in ["🏆", "🆚", "❌"] and reaction.message == notice

        try:
            reaction, _ = await interaction.client.wait_for('reaction_add', check=check, timeout=60)

        # 60秒で処理中止
        except TimeoutError:
            await notice.clear_reactions()
            await notice.reply("Error: Timeout\nもう1度お試しください")
            return

        await notice.delete(delay=1)

        # ❌ならさよなら
        if reaction.emoji == "❌":
            return
        emoji = reaction.emoji

    # エントリーカテゴリー 日本語、英語表記定義
    if role_check[0] or emoji == "🏆":  # ビト森杯
        category = "bitomori"
        category_ja = "ビト森杯"
    elif role_check[1] or emoji == "🆚":  # エキシビション
        category = "exhibition"
        category_ja = "Online Loopstation Exhibition Battle"

    # キャンセル意思の最終確認
    embed = Embed(
        title="エントリーキャンセル",
        description=f"{category_ja}エントリーをキャンセルしますか？\n⭕ `OK`\n❌ このメッセージを削除する",
        color=yellow
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    notice = await interaction.followup.send(embed=embed)
    await notice.add_reaction("⭕")
    await notice.add_reaction("❌")

    def check(reaction, user):
        return user == interaction.user and reaction.emoji in ["⭕", "❌"] and reaction.message == notice

    try:
        reaction, _ = await interaction.client.wait_for('reaction_add', timeout=10, check=check)

    # 10秒で処理中止
    except TimeoutError:
        await notice.clear_reactions()
        await notice.reply("Error: Timeout\nもう1度お試しください")
        return

    await notice.clear_reactions()

    # ❌ならさよなら
    if reaction.emoji == "❌":
        await notice.delete(delay=1)
        return

    # cancel実行
    await entry_cancel(interaction.user, category)


# TODO: 動作テスト
async def button_submission_content(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = interaction.guild.get_member(
        412082841829113877
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
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
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # エントリーしていない
    if any(role_check) is False:

        # エントリー情報詳細のembedを作成
        embed = Embed(
            title="エントリー状況照会",
            description=f"{interaction.user.display_name}さんはエントリーしていません。"
        )
        await interaction.followup.send(embed=embed)
        return

    # 一旦取得中であることを通知
    embed = Embed(
        title="エントリー状況取得中...",
        description="しばらくお待ちください。\n※これには10秒ほどかかります。",
        color=blue
    )
    await interaction.followup.send(embed=embed)

    # DBから取得
    cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索

    # DB登録なし
    if bool(cell_id) is False:
        embed = Embed(
            title="エントリー状況照会",
            color=red
        )
        # とりあえずロールから確認
        if role_check[0]:
            embed.description += "ビト森杯エントリー済み\n"
        elif role_check[1]:
            embed.description += "ビト森杯キャンセル待ち登録済み\n"
        if role_check[2]:
            embed.description += "OLEBエントリー済み\n"

        # ロールの照合結果を送信
        await interaction.followup.send(embed=embed)

        # bot_channelにエラー通知
        await bot_channel.send(f"{tari3210.mention}\nbutton_submission_content Error: DB登録なし\n\n{interaction.channel.jump_url}")
        return

    # DB登録あり
    cell_values = await worksheet.row_values(cell_id.row)  # ユーザーIDの行の値を取得

    # キャンセル待ちの場合、何番目かを取得
    if role_check[1]:

        # キャンセル待ちの順番最初の人を取得
        cell_wait_first = await worksheet.find("キャンセル待ち", in_column=5)

        # キャンセル待ちの順番を取得
        cell_waitlist_position = cell_id.row - cell_wait_first.row + 1
        cell_values[4] += f" {len(role_reserve)}人中 {cell_waitlist_position}番目"

    # エントリー情報詳細のembedを作成
    embed = Embed(
        title="エントリー状況照会",
        description=f"- 名前: {cell_values[2]}\n- 読み: {cell_values[3]}\n- ビト森杯出場可否: {cell_values[4]}\
            \n- OLEB出場可否: {cell_values[5]}\n- デバイス: {cell_values[6]}\n- 備考: {cell_values[7]}\n- 受付時刻: {cell_values[8]}"
    )
    await interaction.channel.send(embed=embed)


# TODO: 動作テスト
async def button_accept_replace(interaction: Interaction):
    await interaction.response.defer(ephemeral=True)
    role = interaction.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    bot_channel = interaction.guild.get_channel(
        897784178958008322  # bot用チャット
    )
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # まず手続き完了通知
    embed = Embed(
        title="繰り上げ出場手続き完了",
        description="手続きが完了しました。ビト森杯ご参加ありがとうございます。\n\n※エントリー状況照会ボタンで確認できるまで、10秒ほどかかります。",
        color=green
    )
    await interaction.followup.send(embed=embed)

    # ロール付け替え
    await interaction.user.remove_roles(role_reserve)
    await interaction.user.add_roles(role)

    # DB更新
    cell_id = await worksheet.find(f'{interaction.user.id}')  # ユーザーIDで検索

    # 出場可否を出場に変更
    await worksheet.update_cell(cell_id.row, 5, "出場")

    # 繰り上げ手続き締切を削除
    await worksheet.update_cell(cell_id.row, 11, "")

    # 時間を追記
    cell_time = await worksheet.cell(row=cell_id.row, col=9)
    await worksheet.update_cell(
        row=cell_time.row,
        col=cell_time.col,
        value=cell_time.value + " 繰り上げ: " +
        datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    )
    # bot_channelへ通知
    embed = Embed(
        title="繰り上げ出場手続き完了",
        description=interaction.channel.jump_url,
        color=green
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url
    )
    await bot_channel.send(embed=embed)
    return
