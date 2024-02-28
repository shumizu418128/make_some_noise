from datetime import datetime, time, timedelta, timezone

from discord import Client, Embed
from discord.ext import tasks

import database
from button_view import get_view
from contact import debug_log, search_contact
from entry import entry_cancel
from database import get_worksheet

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
PM10 = time(22, 0, tzinfo=JST)
AM9 = time(9, 0, tzinfo=JST)
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff

"""
Google spreadsheet
row = 縦 1, 2, 3, ...
col = 横 A, B, C, ...

2024-01-03
ビト森杯関係の定期作業（夜9時）を、すべて10時に変更
ただしadvertise.pyは9時に据え置き
"""


# TODO: このファイル全体 第4回ビト森杯のスプシを作成して、それに合わせて修正する

async def maintenance(client: Client):
    # ビト森杯 進行bot
    bot_notice_channel = client.get_channel(database.CHANNEL_BITOMORI_BOT)

    # ビト森杯
    role_entry = bot_notice_channel.guild.get_role(database.ROLE_LOOP)

    # キャンセル待ち ビト森杯
    role_reserve = bot_notice_channel.guild.get_role(
        database.ROLE_LOOP_RESERVE)

    # エキシビション
    role_OLEB = bot_notice_channel.guild.get_role(database.ROLE_OLEB)

    tari3210 = bot_notice_channel.guild.get_member(database.TARI3210)

    notice = await bot_notice_channel.send("DB定期メンテナンス中...")

    # エントリー名簿取得
    worksheet = await get_worksheet('エントリー名簿')

    # 全登録者のIDと名前を取得（エントリー名簿より）
    DB_all_ids = await worksheet.col_values(10)
    DB_all_names = await worksheet.col_values(3)

    # ビト森杯出場者の情報
    role_entry_ids = [member.id for member in role_entry.members]
    role_entry_names = [member.display_name for member in role_entry.members]
    worksheet_entry = await get_worksheet('ビト森杯出場者一覧')
    DB_entry_ids = await worksheet_entry.col_values(3)
    DB_entry_names = await worksheet_entry.col_values(1)  # いらない？

    # ビト森杯キャンセル待ちの情報
    role_reserve_ids = [member.id for member in role_reserve.members]
    role_reserve_names = [
        member.display_name for member in role_reserve.members]
    worksheet_reserve = await get_worksheet('ビト森杯キャンセル待ち一覧')
    DB_reserve_ids = await worksheet_reserve.col_values(3)
    DB_reserve_names = await worksheet_reserve.col_values(1)  # いらない？

    # OLEB出場者の情報
    role_OLEB_ids = [member.id for member in role_OLEB.members]
    role_OLEB_names = [member.display_name for member in role_OLEB.members]
    worksheet_OLEB = await get_worksheet('OLEB出場者一覧')
    DB_OLEB_ids = await worksheet_OLEB.col_values(3)
    DB_OLEB_names = await worksheet_OLEB.col_values(1)  # いらない？

    # DBリストの最初の要素はヘッダーなので削除
    DB_entry_ids.pop(0)
    DB_entry_names.pop(0)
    DB_reserve_ids.pop(0)
    DB_reserve_names.pop(0)
    DB_OLEB_ids.pop(0)
    DB_OLEB_names.pop(0)
    DB_all_ids.pop(0)
    DB_all_names.pop(0)

    # DBリストからNoneと#N/Aを削除、IDはintに変換
    DB_entry_ids = [
        int(id) for id in DB_entry_ids if id != "" and id != "#N/A"
    ]
    DB_entry_names = [
        name for name in DB_entry_names if name != "" and name != "#N/A"
    ]
    DB_reserve_ids = [
        int(id) for id in DB_reserve_ids if id != "" and id != "#N/A"
    ]
    DB_reserve_names = [
        name for name in DB_reserve_names if name != "" and name != "#N/A"
    ]
    DB_OLEB_ids = [
        int(id) for id in DB_OLEB_ids if id != "" and id != "#N/A"
    ]
    DB_OLEB_names = [
        name for name in DB_OLEB_names if name != "" and name != "#N/A"
    ]
    DB_all_ids = [
        int(id) for id in DB_all_ids if id != "" and id != "#N/A"
    ]
    DB_all_names = [
        name for name in DB_all_names if name != "" and name != "#N/A"
    ]

    # エラーを保存
    errors = []

    # ロール未付与(idベースで確認)
    no_role_ids = set(DB_all_ids) - \
        set(role_entry_ids + role_reserve_ids + role_OLEB_ids)

    for id in no_role_ids:

        # memberを取得
        member = bot_notice_channel.guild.get_member(id)

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
        set(DB_all_ids)

    for id in no_DB_ids:

        # 該当者のmemberオブジェクトを取得
        member = bot_notice_channel.guild.get_member(id)

        # エントリー状況をroleから取得
        role_check = [
            member.get_role(database.ROLE_LOOP),
            member.get_role(database.ROLE_LOOP_RESERVE),
            member.get_role(database.ROLE_OLEB)
        ]
        status = ""
        for role, name in zip(role_check, ["ビト森杯 ", "キャンセル待ち ", "OLEB"]):
            if role:
                status += name

        # エラーを保存
        errors.append(
            f"- DB未登録(エントリー時刻確認) {member.display_name} {member.id} {status}")

    # 名前が一致しているか確認
    wrong_names = set(DB_all_names) - \
        set(role_entry_names + role_reserve_names + role_OLEB_names)

    for name in wrong_names:

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
        embed = Embed(
            title="名前変更検知",
            description="ユーザー名の変更を検知したため、エントリー申請の際に記入した名前に変更しました。\
                イベントの円滑な運営の妨げになるため、ユーザー名の変更はご遠慮ください。\
                \n\n※名前変更をご希望の場合、運営へお問い合わせください。",
            color=red
        )
        await bot_notice_channel.send(member.mention, embed=embed)

        # 問い合わせスレッドでも叱る
        thread = await search_contact(member=member)
        await thread.send(member.mention, embed=embed)

    # 結果通知
    if bool(errors):
        embed = Embed(
            title="DBメンテナンス結果",
            description="\n".join(errors),
            color=red
        )
        embed.set_footer(
            icon_url=bot_notice_channel.guild.icon.url,
            text="第3回ビト森杯\nOnline Loopstation Exhibition Battle"
        )
        embed.timestamp = datetime.now(JST)
        await notice.reply(tari3210.mention, embed=embed)

    else:
        embed = Embed(
            title="DBメンテナンス結果",
            description="エラーはありませんでした。",
            color=green
        )
        embed.set_footer(
            icon_url=bot_notice_channel.guild.icon.url,
            text="第3回ビト森杯\nOnline Loopstation Exhibition Battle"
        )
        embed.timestamp = datetime.now(JST)
        await notice.reply(embed=embed)
    return


async def replacement_expire(client: Client):
    bot_channel = client.get_channel(database.CHANNEL_BOT)

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
        role_check = member_replace.get_role(database.ROLE_LOOP)

        # すでに繰り上げ手続きを完了している場合
        if role_check:
            await debug_log(
                function_name="replacement_expire",
                description="解決済み: 繰り上げ出場手続き完了者のDB未更新を確認",
                color=blue,
                member=member_replace
            )
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
        embed.set_author(
            name=member_replace.display_name,
            icon_url=member_replace.display_avatar.url
        )
        embed.timestamp = datetime.now(JST)
        await thread.send(embed=embed)
        await member_replace.send(embed=embed)
        await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")
        await entry_cancel(member_replace, "bitomori")
    return


# 繰り上げ手続きは毎日22時に実行
async def replacement(client: Client):
    # ビト森杯 進行bot
    bot_channel = client.get_channel(database.CHANNEL_BITOMORI_BOT)

    # ビト森杯
    role = bot_channel.guild.get_role(database.ROLE_LOOP)

    # ビト森杯運営
    admin = bot_channel.guild.get_role(database.ROLE_ADMIN)

    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')

    # 繰り上げ出場手続き中の人の数を取得
    values_status = await worksheet.col_values(5)
    values_status = [
        status for status in values_status if status == "繰り上げ出場手続き中"
    ]
    # 繰り上げ手続き中の枠は確保されている

    # 現在のエントリー数 = エントリー済み + 繰り上げ出場確認中 とする
    entry_count = len(role.members) + len(values_status)

    # 繰り上げ人数が0人以下なら終了（マイナスになる可能性を考慮）
    replace_count = 16 - entry_count
    if replace_count <= 0:
        return

    # キャンセル待ちへの通知(不足人数分for文を回す)
    for _ in range(replace_count):

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

        # 本人の問い合わせthreadへ通知
        embed = Embed(
            title="繰り上げ出場手続きのお願い",
            description=f"エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                繰り上げ出場するためには、手続きが必要です。\
                \n\n```※他の出場希望者の機会確保のため、【72時間以内】の手続きをお願いしています。```\
                \n\n**以下のどちらかのボタンを押してください。**",
            color=yellow
        )
        embed.set_author(
            name=member_replace.display_name,
            icon_url=member_replace.display_avatar.url
        )
        embed.timestamp = datetime.now(JST)
        view = await get_view(replace=True)
        await thread.send(member_replace.mention, embed=embed, view=view)

        # 繰り上げ通知のみ、DMでも送信
        embed = Embed(
            title="🙏ビト森杯 繰り上げ出場手続きのお願い🙏",
            description=f"ビト森杯エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                繰り上げ出場するためには、手続きが必要です。\
                \n\n```※他の出場希望者の機会確保のため、【72時間以内】の手続きをお願いしています。```\
                \n\n【72時間以内】に {thread.jump_url} にて手続きをお願いします。",
            color=yellow
        )
        embed.set_author(
            name=member_replace.display_name,
            icon_url=member_replace.display_avatar.url
        )
        embed.set_footer(
            text="あつまれ！ビートボックスの森",
            icon_url=bot_channel.guild.icon.url
        )
        embed.timestamp = datetime.now(JST)

        try:
            await member_replace.send(member_replace.mention, embed=embed)
            await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")
        except Exception as e:
            await debug_log(
                function_name="replacement",
                description=f"DM送信失敗 {type(e).__name__}\n{str(e)}",
                color=red,
                member=member_replace
            )
        # 海外からのエントリーは運営対処が必要なので、運営へ通知
        locale = thread.name.split("_")[1]  # スレッド名からlocaleを取得
        if locale != "ja":
            await thread.send(f"{admin.mention}\n繰り上げ出場手続き中：海外からのエントリー")

        dt_now = datetime.now(JST)
        dt_limit = dt_now + timedelta(days=3)  # 繰り上げ手続き締切
        limit = dt_limit.strftime("%m/%d")  # 月/日の形式に変換

        # 繰り上げ手続き締切を設定
        await worksheet.update_cell(cell_id.row, 11, limit)

        # 出場可否を繰り上げ出場手続き中に変更
        await worksheet.update_cell(cell_id.row, 5, "繰り上げ出場手続き中")

        # bot用チャットへ通知
        await debug_log(
            function_name="replacement",
            description="繰り上げ出場手続きのお願いを送信",
            color=blue,
            member=member_replace
        )
    return


async def entry_list_update(client: Client):
    # ビト森杯 進行bot
    bot_notice_channel = client.get_channel(database.CHANNEL_BITOMORI_BOT)

    # ビト森杯
    role = bot_notice_channel.guild.get_role(database.ROLE_LOOP)

    # エントリー名簿を取得
    entry_list = [member.display_name for member in role.members]

    # いないなら終了
    if bool(entry_list) is False:
        return

    # ビト森杯botチャンネルへ送信
    embed = Embed(
        title="現時点でのビト森杯参加者一覧",
        description="\n".join(entry_list),
        color=blue
    )
    embed.set_footer(
        icon_url=bot_notice_channel.guild.icon.url,
        text="第3回ビト森杯"
    )
    embed.timestamp = datetime.now(JST)
    await bot_notice_channel.send(embed=embed)
    return


# 24時間前に繰り上げ出場手続きのお願いを再度送信
async def replacement_notice_24h(client: Client):
    bot_channel = client.get_channel(database.CHANNEL_BOT)

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
        role_check = member_replace.get_role(database.ROLE_LOOP)

        # すでに繰り上げ手続きを完了している場合
        if role_check:
            await debug_log(
                function_name="replacement_notice_24h",
                description="解決済み: 繰り上げ出場手続き完了者のDB未更新を確認",
                color=blue,
                member=member_replace
            )
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
                \n\n```※他の出場希望者の機会確保のため、【72時間以内】の手続きをお願いしています。```\
                \n\n【72時間以内】に手続きをお願いします。",
            color=red
        )
        embed.set_author(
            name=member_replace.display_name,
            icon_url=member_replace.display_avatar.url
        )
        embed.set_footer(
            icon_url=bot_channel.guild.icon.url,
            text="第3回ビト森杯"
        )
        embed.timestamp = datetime.now(JST)

        # viewを作成
        view = await get_view(replace=True)

        # 問い合わせthreadに送信
        await thread.send(f"{member_replace.mention}\n# 明日22時締切", embed=embed)
        await thread.send("以下のどちらかのボタンを押してください。", view=view)

        # DMでも送信
        try:
            await member_replace.send(f"{member_replace.mention}\n# 明日22時締切", embed=embed)
            await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")
        except Exception as e:
            await debug_log(
                function_name="replacement_notice_24h",
                description=f"DM送信失敗 {type(e).__name__}\n{str(e)}",
                color=red,
                member=member_replace
            )
    return


@tasks.loop(time=PM10)
async def daily_work_PM10(client: Client):
    dt_now = datetime.now(JST)
    dt_day1 = datetime(
        year=2024,
        month=2,
        day=17,
        tzinfo=JST
    )
    # 繰り上げ出場手続きのお願い(2/16 22:00まで)
    if dt_now < dt_day1:
        await replacement_expire(client)
        await replacement(client)
        await replacement_notice_24h(client)


@tasks.loop(time=AM9)
async def daily_work_AM9(client: Client):
    await maintenance(client)
    await entry_list_update(client)
