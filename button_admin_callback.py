import re
from datetime import datetime, timedelta, timezone

from discord import ChannelType, Embed, Interaction

from contact import (contact_start, debug_log, get_submission_embed,
                     get_worksheet, search_contact)
from entry import entry_cancel

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff


async def button_admin_entry(interaction: Interaction):

    # 応答タイミングが状況に応じて違うので、ここで応答を済ませる
    await interaction.response.send_message(f"{interaction.user.mention}\n処理中...", delete_after=2)

    role = interaction.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = interaction.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    role_exhibition = interaction.guild.get_role(
        1171760161778581505  # エキシビション
    )
    category = interaction.data["custom_id"].replace(
        "button_admin_entry_", "").replace("button_entry_", "")  # "bitomori" or "exhibition"

    # エントリーの対象者を取得
    # thread内なら名前から、それ以外なら入力させる
    if interaction.channel.type == ChannelType.private_thread:  # ビト森杯 問合せ
        member_id = interaction.channel.name.split("_")[0]
        member = interaction.guild.get_member(int(member_id))

    else:
        notice = await interaction.channel.send("↓ID入力↓")

        # 正規表現で複数桁の数字かどうか判定
        def check(message):
            return bool(re.match(r"^[0-9]{17,}$", message.content)) and message.channel == interaction.channel and message.author == interaction.user

        try:
            # 1分待機
            msg = await interaction.client.wait_for('message', check=check, timeout=60)
        except TimeoutError:  # 1分経過ならさよなら
            await notice.delete()
            return

        await msg.add_reaction("✅")

        member = interaction.guild.get_member(int(msg.content))

    if member is None:
        await interaction.channel.send("Error: ユーザーが見つかりませんでした", ephemeral=True)
        return

    # ビト森杯エントリー済みか確認
    role_check = [
        any([
            member.get_role(
                1036149651847524393  # ビト森杯
            ),
            member.get_role(
                1172542396597289093  # キャンセル待ち ビト森杯
            )
        ]),
        member.get_role(
            1171760161778581505  # エキシビション
        )
    ]
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # エントリー済みか確認
    # ビト森杯エントリー済み
    if role_check[0] and category == "bitomori":
        embed = Embed(
            title="エントリー済み",
            description="ビト森杯\nすでにエントリー済みです。",
            color=red
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url
        )
        await interaction.channel.send(embed=embed, ephemeral=True)
        return

    # エキシビションエントリー済み
    if role_check[1] and category == "exhibition":
        embed = Embed(
            title="エントリー済み",
            description="Online Loopstation Exhibition Battle\nすでにエントリー済みです。",
            color=red
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url
        )
        await interaction.channel.send(embed=embed, ephemeral=True)
        return

    # エントリー処理(名前以外すべて空欄)
    # エントリー数が上限に達している or キャンセル待ちリストに人がいる場合
    if any([len(role.members) >= 16, len(role_reserve.members) > 0]):
        await member.add_roles(role_reserve)
        status = "キャンセル待ち"

    # ビト森杯
    elif category == "bitomori":
        await member.add_roles(role)
        status = "出場"

    # OLEB
    elif category == "exhibition":
        await member.add_roles(role_exhibition)
        status = "参加"

    # 問い合わせスレッドを作成or取得
    thread = await search_contact(member, create=True)

    # DBに登録済みか確認
    cell_id = await worksheet.find(f'{member.id}')

    # DB登録済みの場合、通常エントリー処理できるので仮登録扱いしない
    if bool(cell_id):

        # 本登録できた旨を通知
        await interaction.channel.send(f"{interaction.user.mention}\nエントリー処理完了: {member.display_name}さん")

        # 備考取得
        cell_note = await worksheet.cell(row=cell_id.row, col=8)

        # エントリー情報・備考を更新
        # ビト森杯の場合
        if category == "bitomori":
            await worksheet.update_cell(row=cell_id.row, col=5, value=status)

            # 備考に "運営側で登録" と書き込み
            await worksheet.update_cell(row=cell_id.row, col=8, value=f"{cell_note.value} 運営側でビト森杯エントリー登録")

        # エキシビションの場合
        elif category == "exhibition":
            await worksheet.update_cell(row=cell_id.row, col=6, value=status)

            # 備考に "運営側で登録" と書き込み
            await worksheet.update_cell(row=cell_id.row, col=8, value=f"{cell_note.value} 運営側でOLEBエントリー登録")

        # 受付時刻を更新
        await worksheet.update_cell(row=cell_id.row, col=9, value=str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")))

        # 対象者に通知
        await thread.send(f"運営側で {member.mention} さんに対し、エントリー処理を行いました。")
        await contact_start(interaction.client, member, entry_redirect=True)

        # bot用チャットに通知
        await debug_log(
            function_name=f"button_admin_entry_{category}",
            description="エントリー処理完了",
            color=blue,
            member=member
        )
        return

    # DB登録なしの場合、新規登録
    else:

        # ボタンを押した人に通知
        await interaction.channel.send(f"{interaction.user.mention}\n仮登録完了\n{member.display_name}さん")

        # エントリー数を更新
        num_entries = await worksheet.cell(row=3, col=1)
        num_entries.value = int(num_entries.value) + 1
        await worksheet.update_cell(row=3, col=1, value=str(num_entries.value))
        row = int(num_entries.value) + 1

        # 名前を書き込み
        await worksheet.update_cell(row=row, col=3, value=member.display_name)

        # 参加状況を書き込み
        # ビト森杯の場合
        if category == "bitomori":
            await worksheet.update_cell(row=row, col=5, value=status)

        # エキシビションの場合
        elif category == "exhibition":
            await worksheet.update_cell(row=row, col=6, value=status)

        # 備考に "仮登録" を書き込み
        await worksheet.update_cell(row=row, col=8, value="仮登録")

        # 受付時刻、IDを書き込み
        await worksheet.update_cell(row=row, col=9, value=str(datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")))
        await worksheet.update_cell(row=row, col=10, value=str(member.id))

        # 対象者に通知
        await thread.send(
            f"{member.mention} さんのエントリー仮登録を行いました。\
            \n後ほど運営より、エントリーに必要な情報をお伺いします。しばらくお待ちください。"
        )
        # bot用チャットに通知
        await debug_log(
            function_name=f"button_admin_entry_{category}",
            description="仮登録完了\nよみがな・デバイス・備考 要記入",
            color=yellow,
            member=member
        )
        return


async def button_admin_cancel(interaction: Interaction):

    # 応答タイミングが状況に応じて違うので、ここで応答を済ませる
    await interaction.response.send_message(f"{interaction.user.mention}\n処理中...", delete_after=2)

    # 対象者を取得
    # thread内なら名前から、それ以外なら入力させる
    if interaction.channel.type == ChannelType.private_thread:  # ビト森杯 問合せ
        member_id = interaction.channel.name.split("_")[0]
        member = interaction.guild.get_member(int(member_id))

    else:
        notice = await interaction.channel.send("↓ID入力↓")

        # 正規表現で複数桁の数字かどうか判定
        def check(message):
            return bool(re.match(r"^[0-9]{17,}$", message.content)) and message.channel == interaction.channel and message.author == interaction.user

        try:
            # 1分待機
            msg = await interaction.client.wait_for('message', check=check, timeout=60)
        except TimeoutError:  # 1分経過ならさよなら
            await notice.delete()
            return

        await msg.add_reaction("✅")

        member = interaction.guild.get_member(int(msg.content))

    if member is None:
        await interaction.channel.send("Error: ユーザーが見つかりませんでした")
        return

    role_check = [
        any([
            member.get_role(
                1036149651847524393  # ビト森杯
            ),
            member.get_role(
                1172542396597289093  # キャンセル待ち ビト森杯
            )
        ]),
        member.get_role(
            1171760161778581505  # エキシビション
        )
    ]
    # どのロールも持っていない場合
    if any(role_check) is False:
        embed = Embed(
            title="エントリーキャンセル",
            description=f"Error: {member.display_name}さんはエントリーしていません。",
            color=red
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url
        )
        await interaction.channel.send(embed=embed)
        return

    # エントリーカテゴリー 日本語、英語表記定義
    if role_check[0]:  # ビト森杯
        category = "bitomori"
        category_ja = "ビト森杯"
    if role_check[1]:  # エキシビション
        category = "exhibition"
        category_ja = "Online Loopstation Exhibition Battle"

    # 両方にエントリーしている場合
    if all(role_check):

        # キャンセルするカテゴリーを選択
        embed = Embed(
            title="エントリーキャンセル",
            description="どちらのエントリーをキャンセルしますか？\n🏆 ビト森杯\
                \n⚔️ Online Loopstation Exhibition Battle\n❌ このメッセージを削除する",
            color=yellow
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url
        )
        notice = await interaction.channel.send(interaction.user.mention, embed=embed)
        await notice.add_reaction("🏆")
        await notice.add_reaction("⚔️")
        await notice.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and reaction.emoji in ["🏆", "⚔️", "❌"] and reaction.message == notice

        try:
            reaction, _ = await interaction.client.wait_for('reaction_add', check=check, timeout=60)

        # 60秒で処理中止
        except TimeoutError:
            await notice.delete()
            await interaction.channel.send("Error: Timeout\nもう1度お試しください")
            return

        # リアクションを消す
        await notice.clear_reactions()

        # ❌ならさよなら
        if reaction.emoji == "❌":
            return
        emoji = reaction.emoji

        # エントリーカテゴリー 日本語、英語表記定義
        if emoji == "🏆":  # ビト森杯
            category = "bitomori"
            category_ja = "ビト森杯"

        if emoji == "⚔️":  # エキシビション
            category = "exhibition"
            category_ja = "Online Loopstation Exhibition Battle"

    # キャンセル意思の最終確認
    embed = Embed(
        title="エントリーキャンセル",
        description=f"{category_ja}エントリーをキャンセルしますか？\n⭕ `OK`\n❌ このメッセージを削除する",
        color=yellow
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url
    )
    notice = await interaction.channel.send(interaction.user.mention, embed=embed)
    await notice.add_reaction("⭕")
    await notice.add_reaction("❌")

    def check(reaction, user):
        return user == interaction.user and reaction.emoji in ["⭕", "❌"] and reaction.message == notice

    try:
        reaction, _ = await interaction.client.wait_for('reaction_add', timeout=10, check=check)

    # 10秒で処理中止
    except TimeoutError:
        await notice.delete()
        await interaction.channel.send("Error: Timeout\nもう1度お試しください")
        return

    await notice.clear_reactions()

    # ❌ならさよなら
    if reaction.emoji == "❌":
        await notice.delete(delay=1)
        return

    # cancel実行
    await entry_cancel(member, category)


async def button_admin_create_thread(interaction: Interaction):
    notice = await interaction.response.send_message("↓ID入力↓")

    # 正規表現で複数桁の数字かどうか判定
    def check(message):
        return bool(re.match(r"^[0-9]{17,}$", message.content)) and message.channel == interaction.channel and message.author == interaction.user

    try:
        # 1分待機
        msg = await interaction.client.wait_for('message', check=check, timeout=60)
    except TimeoutError:  # 1分経過ならさよなら
        await notice.delete()
        return

    await msg.add_reaction("✅")

    member = interaction.guild.get_member(int(msg.content))

    if member is None:
        await interaction.channel.send("Error: ユーザーが見つかりませんでした", ephemeral=True)
        return

    # 問い合わせスレッドを作成or取得
    thread = await search_contact(member, create=True)
    embed = Embed(
        title="問い合わせスレッド作成",
        description=f"{member.display_name}さんの問い合わせスレッドを作成しました。\n{thread.jump_url}",
        color=blue
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.avatar.url
    )
    await interaction.channel.send(embed=embed)

    await contact_start(interaction.client, member)
    return


async def button_admin_submission_content(interaction: Interaction):

    # 応答タイミングが状況に応じて違うので、ここで応答を済ませる
    await interaction.response.send_message(f"{interaction.user.mention}\n処理中...", delete_after=2)

    # 対象者を取得
    # thread内なら名前から、それ以外なら入力させる
    if interaction.channel.type == ChannelType.private_thread:  # ビト森杯 問合せ
        member_id = interaction.channel.name.split("_")[0]
        member = interaction.guild.get_member(int(member_id))

    else:
        notice = await interaction.channel.send("↓ID入力↓")

        # 正規表現で複数桁の数字かどうか判定
        def check(message):
            return bool(re.match(r"^[0-9]{17,}$", message.content)) and message.channel == interaction.channel and message.author == interaction.user

        try:
            # 1分待機
            msg = await interaction.client.wait_for('message', check=check, timeout=60)
        except TimeoutError:  # 1分経過ならさよなら
            await notice.delete()
            return

        await msg.add_reaction("✅")

        member = interaction.guild.get_member(int(msg.content))

    if member is None:
        await interaction.channel.send("Error: ユーザーが見つかりませんでした")
        return

    embed = await get_submission_embed(member)
    await interaction.channel.send(interaction.user.mention, embed=embed)
    return
