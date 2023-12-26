from datetime import datetime, time, timedelta, timezone

from discord import Client, Embed
from discord.ext import tasks

from button_view import get_view
from contact import get_worksheet, search_contact
from entry import entry_cancel

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)
AM9 = time(9, 0, tzinfo=JST)
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
async def maintenance(client: Client):
    bot_notice_channel = client.get_channel(
        916608669221806100  # ビト森杯 進行bot
    )
    role_entry = bot_notice_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = bot_notice_channel.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    role_OLEB = bot_notice_channel.guild.get_role(
        1171760161778581505  # エキシビション
    )
    tari3210 = bot_notice_channel.guild.get_member(
        412082841829113877
    )
    # エントリー名簿取得
    worksheet = await get_worksheet('エントリー名簿')

    # ビト森杯出場者の情報
    role_entry_ids = [member.id for member in role_entry.members]
    role_entry_names = [member.display_name for member in role_entry.members]
    worksheet_entry = await get_worksheet('ビト森杯出場者一覧')
    DB_entry_ids = await worksheet_entry.col_values(3)
    DB_entry_names = await worksheet_entry.col_values(1)

    # ビト森杯キャンセル待ちの情報
    role_reserve_ids = [member.id for member in role_reserve.members]
    role_reserve_names = [
        member.display_name for member in role_reserve.members]
    worksheet_reserve = await get_worksheet('ビト森杯キャンセル待ち一覧')
    DB_reserve_ids = await worksheet_reserve.col_values(3)
    DB_reserve_names = await worksheet_reserve.col_values(1)

    # OLEB出場者の情報
    role_OLEB_ids = [member.id for member in role_OLEB.members]
    role_OLEB_names = [member.display_name for member in role_OLEB.members]
    worksheet_OLEB = await get_worksheet('OLEB出場者一覧')
    DB_OLEB_ids = await worksheet_OLEB.col_values(3)
    DB_OLEB_names = await worksheet_OLEB.col_values(1)

    # DBリストの最初の要素はヘッダーなので削除
    DB_entry_ids.pop(0)
    DB_entry_names.pop(0)
    DB_reserve_ids.pop(0)
    DB_reserve_names.pop(0)
    DB_OLEB_ids.pop(0)
    DB_OLEB_names.pop(0)

    # DBリストからNoneを削除
    DB_entry_ids = [id for id in DB_entry_ids if id != ""]
    DB_entry_names = [name for name in DB_entry_names if name != ""]
    DB_reserve_ids = [id for id in DB_reserve_ids if id != ""]
    DB_reserve_names = [name for name in DB_reserve_names if name != ""]
    DB_OLEB_ids = [id for id in DB_OLEB_ids if id != ""]
    DB_OLEB_names = [name for name in DB_OLEB_names if name != ""]

    # エラーを保存
    errors = []
    notice = await bot_notice_channel.send("DB定期メンテナンス中...")

    # ロール未付与(idベースで確認)
    no_role_ids = set(DB_entry_ids + DB_reserve_ids + DB_OLEB_ids) - \
        set(role_entry_ids + role_reserve_ids + role_OLEB_ids)

    for id in no_role_ids:

        # memberを取得
        member = bot_notice_channel.guild.get_member(int(id))

        # ビト森杯キャンセル待ちか、繰り上げ出場手続き中の場合
        if id in DB_reserve_ids:

            # ロール付与
            await member.add_roles(role_reserve)

            # エラーを保存
            errors.append(
                f"- 解決済み：キャンセル待ちロール未付与 {member.display_name} {member.id}"
            )
        # ビト森杯出場者の場合
        if id in DB_entry_ids:

            # ロール付与
            await member.add_roles(role_entry)

            # エラーを保存
            errors.append(
                f"- 解決済み：エントリーロール未付与 {member.display_name} {member.id}"
            )
        # OLEB出場者の場合
        if id in DB_OLEB_ids:

            # ロール付与
            await member.add_roles(role_OLEB)

            # エラーを保存
            errors.append(
                f"- 解決済み：OLEBロール未付与 {member.display_name} {member.id}"
            )

    # DB未登録(idベースで確認)
    no_DB_ids = set(role_entry_ids + role_reserve_ids + role_OLEB_ids) - \
        set(DB_entry_ids + DB_reserve_ids + DB_OLEB_ids)

    for id in no_DB_ids:

        # 該当者のmemberオブジェクトを取得
        member = bot_notice_channel.guild.get_member(int(id))

        # エントリー状況をroleから取得
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
        status = ""
        for role, name in zip(role_check, ["ビト森杯 ", "キャンセル待ち ", "OLEB"]):
            if role:
                status += name

        # エラーを保存
        errors.append(
            f"- DB未登録(エントリー時刻確認) {member.display_name} {member.id} {status}")

    # 名前が一致しているか確認
    for name in set(DB_entry_names + DB_reserve_names + DB_OLEB_names) - set(role_entry_names + role_reserve_names + role_OLEB_names):

        # 該当者のセルを取得
        cell_name = await worksheet.find(name)

        # 該当者のユーザーID、memberオブジェクトを取得
        cell_id = await worksheet.cell(row=cell_name.row, col=10)
        member = bot_notice_channel.guild.get_member(int(cell_id.value))

        # ユーザー名を変更
        member = await member.edit(nick=name)

        # エラーを保存
        errors.append(f"- 解決済み：名前変更検知 {member.display_name} {member.id}")

        # ビト森杯botチャンネルで叱る
        await bot_notice_channel.send(
            f"{member.mention}\nユーザー名の変更を検知したため、エントリー申請の際に記入した名前に変更しました。\
            \n\nユーザー名の変更はご遠慮ください。"
        )
    # 結果通知
    if bool(errors):
        embed = Embed(
            title="DBメンテナンス結果",
            description="\n".join(errors),
            color=red
        )
        await notice.reply(tari3210.mention, embed=embed)

    else:
        embed = Embed(
            title="DBメンテナンス結果",
            description="エラーはありませんでした。",
            color=green
        )
        await notice.reply(embed=embed)


# TODO: 動作テスト
async def replacement_expire(client: Client):
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = bot_channel.guild.get_member(
        412082841829113877
    )
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # 今日の日付をstrで取得
    dt_now = datetime.now(JST)
    today = dt_now.strftime("%m/%d")  # 月/日の形式に変換

    # 繰り上げ締切が今日のセルを取得
    cell_list_deadline = await worksheet.findall(today, in_column=11)

    # 1人ずつキャンセルする
    for cell in cell_list_deadline:

        # ユーザーIDを取得
        cell_id = await worksheet.cell(row=cell.row, col=10)

        # 問い合わせスレッドを取得
        member_replace = bot_channel.guild.get_member(int(cell_id.value))
        thread = await search_contact(member=member_replace)

        # 繰り上げ手続き済みか確認
        role_check = member_replace.get_role(
            1036149651847524393  # ビト森杯
        )
        # すでに繰り上げ手続きを完了している場合
        if role_check:
            await bot_channel.send(f"{tari3210.mention}\n解決済み: 繰り上げ出場手続き完了者のDB未更新を確認\n{thread.jump_url}")

            # 繰り上げ手続き締切を空白に変更
            await worksheet.update_cell(cell.row, cell.col, "")

            # 出場可否を出場に変更
            await worksheet.update_cell(cell.row, 5, "出場")
            continue

        # キャンセル通知
        embed = Embed(
            title="ビト森杯 キャンセル通知",
            description="ビト森杯 繰り上げ出場手続きのお願いを送信しましたが、72時間以内に返答がなかったため、キャンセルとみなします。\
                \n\n※エントリー手続きを行えば、再度キャンセル待ち登録は可能ですが、キャンセル待ちの最後尾に追加されます。",
            color=red
        )
        await thread.send(embed=embed)
        await member_replace.send(embed=embed)
        await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")
        await entry_cancel(member_replace)


# TODO: 動作テスト
# 繰り上げ手続きは毎日21時に実行
async def replacement(client: Client):
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    role = bot_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = bot_channel.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    admin = bot_channel.guild.get_role(
        904368977092964352  # ビト森杯運営
    )
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # 繰り上げ出場手続き中の人の数を取得
    values_status = await worksheet.col_values(5)
    values_status = [
        status for status in values_status if status == "繰り上げ出場手続き中"
    ]
    # 繰り上げ手続き中の枠は確保されている

    # エントリー済み + 繰り上げ出場確認中 = 現在のエントリー数とする
    entry_count = len(role.members) + len(values_status)

    # キャンセル待ちへの通知
    for _ in range(16 - entry_count):

        # entry_countが16人を下回り、かつキャンセル待ちがいる場合
        if len(role_reserve.members) > 0:

            # キャンセル待ちの順番最初の人を取得
            cell_waitlist_first = await worksheet.find("キャンセル待ち", in_column=5)

            # いないなら終了
            if bool(cell_waitlist_first) is False:
                break

            # ユーザーID、memberを取得
            cell_id = await worksheet.cell(row=cell_waitlist_first.row, col=10)
            member_replace = bot_channel.guild.get_member(int(cell_id.value))

            # 問い合わせスレッドを取得
            thread = await search_contact(member=member_replace)

            # bot_channelへ通知
            embed = Embed(
                title="繰り上げ出場通知を送信 (出場意思確認中)",
                description=thread.jump_url,
                color=blue
            )
            embed.set_author(
                name=member_replace.display_name,
                icon_url=member_replace.avatar.url
            )
            await bot_channel.send(embed=embed)

            # 本人の問い合わせthreadへ通知
            embed = Embed(
                title="繰り上げ出場通知",
                description=f"エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                    繰り上げ出場するためには、手続きが必要です。\
                    \n\n```※他の出場希望者の機会確保のため、__72時間以内__の手続きをお願いしています。```\
                    \n\n**以下のどちらかのボタンを押してください。**",
                color=yellow
            )
            view = await get_view(replace=True)
            await thread.send(member_replace.mention, embed=embed, view=view)

            # 繰り上げ通知のみ、DMでも送信
            embed = Embed(
                title="🙏ビト森杯 繰り上げ出場手続きのお願い🙏",
                description=f"ビト森杯エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                    繰り上げ出場するためには、手続きが必要です。\
                    \n\n```※他の出場希望者の機会確保のため、__72時間以内__の手続きをお願いしています。```\
                    \n\n__72時間以内__に {thread.jump_url} にて手続きをお願いします。",
                color=yellow
            )
            embed.set_author(
                name="あつまれ！ビートボックスの森",
                icon_url=bot_channel.guild.icon.url
            )
            await member_replace.send(member_replace.mention, embed=embed)
            await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")

            # 海外からのエントリーは運営対処が必要なので、運営へ通知
            locale = thread.name.split("_")[1]  # スレッド名からlocaleを取得
            if locale != "ja":
                await thread.send(f"{admin.mention}\n繰り上げ出場手続き中：海外からのエントリー")

            dt_now = datetime.now(JST)
            dt_limit = dt_now + timedelta(days=3)  # 繰り上げ手続き締切
            limit = dt_limit.strftime("%m/%d")  # 月/日の形式に変換

            # ユーザーIDのセルを取得
            cell_id = await worksheet.find(f'{member_replace.id}')

            # 繰り上げ手続き締切を設定
            await worksheet.update_cell(cell_id.row, 11, limit)

            # 出場可否を繰り上げ出場手続き中に変更
            await worksheet.update_cell(cell_id.row, 5, "繰り上げ出場手続き中")


# TODO: 動作テスト
async def entry_list_update(client: Client):
    bot_notice_channel = client.get_channel(
        916608669221806100  # ビト森杯 進行bot
    )
    role = bot_notice_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )

    # 今日の日付をdatetimeで取得
    dt_now = datetime.now(JST)

    # エントリー名簿を取得
    entry_list = [member.display_name for member in role.members]

    # ビト森杯botチャンネルへ送信
    embed = Embed(
        title="現時点でのビト森杯参加者一覧",
        description="\n".join(entry_list),
        color=blue
    )
    embed.timestamp = dt_now
    await bot_notice_channel.send(embed=embed)


# TODO: 動作テスト
# 24時間前に繰り上げ出場手続きのお願いを再度送信
async def replacement_notice_24h(client: Client):
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    tari3210 = bot_channel.guild.get_member(
        412082841829113877
    )
    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # 明日の日付をstrで取得
    dt_tomorrow = datetime.now(JST) + timedelta(days=1)
    tomorrow = dt_tomorrow.strftime("%m/%d")  # 月/日の形式に変換

    # 繰り上げ締切が明日のセルを取得
    cell_list_deadline_tomorrow = await worksheet.findall(tomorrow, in_column=11)

    # いないなら終了
    if bool(cell_list_deadline_tomorrow) is False:
        return

    # 1人ずつ通知する
    for cell in cell_list_deadline_tomorrow:

        # ユーザーIDを取得
        cell_id = await worksheet.cell(row=cell.row, col=10)

        # memberオブジェクトと、その人の問い合わせthreadを取得
        member_replace = bot_channel.guild.get_member(int(cell_id.value))
        thread = await search_contact(member=member_replace)

        # 繰り上げ手続き済みか確認
        role_check = member_replace.get_role(
            1036149651847524393  # ビト森杯
        )
        # すでに繰り上げ手続きを完了している場合
        if role_check:
            await bot_channel.send(f"{tari3210.mention}\n解決済み: 繰り上げ出場手続き完了者のDB未更新を確認\n{thread.jump_url}")

            # 繰り上げ手続き締切を空白に変更
            await worksheet.update_cell(cell.row, cell.col, "")

            # 出場可否を出場に変更
            await worksheet.update_cell(cell.row, 5, "出場")
            continue

        # 通知embedを作成
        embed = Embed(
            title="🙏ビト森杯 繰り上げ出場手続きのお願い🙏",
            description=f"ビト森杯エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                繰り上げ出場するためには、手続きが必要です。\
                \n\n```※他の出場希望者の機会確保のため、__72時間以内__の手続きをお願いしています。```\
                \n\n__72時間以内__に手続きをお願いします。",
            color=red
        )
        # viewを作成
        view = await get_view(replace=True)

        # 問い合わせthreadに送信
        await thread.send(f"{member_replace.mention}\n# 明日21時締切", embed=embed)
        await thread.send("以下のどちらかのボタンを押してください。", view=view)

        # DMでも送信
        await member_replace.send(f"{member_replace.mention}\n# 明日21時締切", embed=embed)
        await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")


@tasks.loop(time=PM9)
async def daily_work_PM9(client: Client):
    dt_now = datetime.now(JST)
    dt_day1 = datetime(
        year=2024,
        month=2,
        day=17,
        tzinfo=JST
    )
    # 繰り上げ出場手続きのお願い(2/16 21:00まで)
    if dt_now < dt_day1:
        await replacement_expire(client)
        await replacement(client)
        await replacement_notice_24h(client)


@tasks.loop(time=AM9)
async def daily_work_AM9(client: Client):
    await maintenance(client)
    await entry_list_update(client)
