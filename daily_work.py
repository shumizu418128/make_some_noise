from datetime import datetime, time, timedelta, timezone

from discord import Client, Embed
from discord.ext import tasks

from button_view import get_view
from contact import get_worksheet, search_contact
from entry import entry_cancel

# NOTE: ビト森杯運営機能搭載ファイル
JST = timezone(timedelta(hours=9))
PM9 = time(21, 0, tzinfo=JST)
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
    bot_channel = client.get_channel(
        897784178958008322  # bot用チャット
    )
    bot_notice_channel = client.get_channel(
        916608669221806100  # ビト森杯 進行bot
    )
    # discordからの情報
    role_entry = bot_channel.guild.get_role(
        1036149651847524393  # ビト森杯
    )
    role_reserve = bot_channel.guild.get_role(
        1172542396597289093  # キャンセル待ち ビト森杯
    )
    tari3210 = bot_channel.guild.get_member(
        412082841829113877
    )
    entry_names = [member.display_name for member in role_entry.members]
    reserve_names = [member.display_name for member in role_reserve.members]
    entry_ids = [member.id for member in role_entry.members]
    reserve_ids = [member.id for member in role_reserve.members]

    # Google spreadsheet worksheet読み込み
    worksheet = await get_worksheet('エントリー名簿')
    DB_names = await worksheet.col_values(3)
    DB_ids = await worksheet.col_values(10)

    errors = []

    notice = await bot_channel.send("DB定期メンテナンス中...")

    # ロール未付与(idベースで確認)
    for id in set(DB_ids) - set(entry_ids) - set(reserve_ids):

        # ロール未付与のユーザーIDを取得
        cell_id = await worksheet.find(id)

        # エントリー状況、memberを取得
        cell_status = await worksheet.cell(row=cell_id.row, col=5)
        member = bot_channel.guild.get_member(int(id))

        # キャンセル待ちか、繰り上げ出場手続き中の場合
        if cell_status.value in ["キャンセル待ち", "繰り上げ出場手続き中"]:

            # ロール付与
            await member.add_roles(role_reserve)

            # エラーを保存
            errors.append(
                f"- 解決済み：キャンセル待ちロール未付与 {member.display_name} {member.id}"
            )
        # 出場の場合
        if cell_status.value == "出場":

            # ロール付与
            await member.add_roles(role_entry)

            # エラーを保存
            errors.append(
                f"- 解決済み：エントリーロール未付与 {member.display_name} {member.id}"
            )

    # DB未登録(idベースで確認)
    for id in set(entry_ids) + set(reserve_ids) - set(DB_ids):

        # 該当者のmemberオブジェクトを取得
        member = bot_channel.guild.get_member(int(id))

        # エラーを保存
        errors.append(f"- DB未登録(エントリー時刻確認) {member.display_name} {member.id}")

    # 名前が一致しているか確認
    for name in set(DB_names) - set(entry_names + reserve_names):

        # 該当者のセルを取得
        cell_name = await worksheet.find(name)

        # 該当者のユーザーID、memberオブジェクトを取得
        cell_id = await worksheet.cell(row=cell_name.row, col=10)
        member = bot_channel.guild.get_member(
            int(cell_id.value)
        )
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

        # 通知
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
        status for status in values_status if status == "繰り上げ出場手続き中"  # 繰り上げ出場手続き中の人を取得
    ]
    # 繰り上げ手続き中の枠は確保されている

    # エントリー済み + 繰り上げ出場確認中 = 現在のエントリー数とする
    entry_count = len(role.members) + len(values_status)

    # キャンセル待ちへの通知
    for _ in range(16 - entry_count):  # entry_countが16人を下回り

        # かつキャンセル待ちがいる場合
        if len(role_reserve.members) > 0:

            # キャンセル待ちの順番最初の人を取得
            cell_waitlist_first = await worksheet.find("キャンセル待ち", in_column=5)

            # ユーザーID、memberを取得
            cell_id = await worksheet.cell(row=cell_waitlist_first.row, col=10)
            member_replace = bot_channel.guild.get_member(int(cell_id.value))

            # 問い合わせスレッドを取得
            thread = await search_contact(member=member_replace)

            # bot_channelへ通知
            embed = Embed(
                title="繰り上げエントリー確認中",
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
                    \n\n以下のどちらかのボタンを押してください。",
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

            # 海外からのエントリー
            locale = thread.name.split("_")[1]  # スレッド名からlocaleを取得
            if locale != "ja":
                await thread.send(f"{admin.mention}\n繰り上げ出場手続き中：海外からのエントリー")

            dt_now = datetime.now(JST)
            dt_limit = dt_now + timedelta(days=3)  # 繰り上げ手続き締切
            limit = dt_limit.strftime("%m/%d")  # 月/日の形式に変換

            cell_id = await worksheet.find(f'{member_replace.id}')  # ユーザーIDで検索
            await worksheet.update_cell(cell_id.row, 11, limit)  # 繰り上げ手続き締切を設定

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

    # 送信
    embed = Embed(
        title="参加者一覧",
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

    # 1人ずつ通知する
    for cell in cell_list_deadline_tomorrow:

        # ユーザーIDを取得
        cell_id = await worksheet.cell(row=cell.row, col=10)

        # memberオブジェクトと、その人の問い合わせthreadを取得
        member_replace = bot_channel.guild.get_member(int(cell_id.value))
        thread = await search_contact(member=member_replace)

        # エントリー済みか確認
        role_check = member_replace.get_role(
            1036149651847524393  # ビト森杯
        )
        # すでに繰り上げ手続きを完了している場合
        if role_check:
            await bot_channel.send(f"{tari3210.mention}\n繰り上げ出場手続き完了者のDB未更新を確認\n{thread.jump_url}")
            await worksheet.update_cell(cell.row, cell.col, "出場")  # 出場可否を出場に変更
            continue

        # 通知embedを作成
        embed = Embed(
            title="🙏ビト森杯 繰り上げ出場手続きのお願い🙏",
            description=f"ビト森杯エントリーをキャンセルした方がいたため、{member_replace.display_name}さんは繰り上げ出場できます。\
                繰り上げ出場するためには、手続きが必要です。\
                \n\n```※他の出場希望者の機会確保のため、__72時間以内__の手続きをお願いしています。```\
                \n\n__72時間以内__に {thread.jump_url} にて手続きをお願いします。\n",
            color=red
        )
        # viewを作成
        view = await get_view(replace=True)

        # 送信
        await thread.send(f"{member_replace.mention}\n# 明日21時締切", embed=embed, view=view)
        await member_replace.send(f"{member_replace.mention}\n# 明日21時締切", embed=embed)
        await member_replace.send("### このDMは送信専用です。ここに何も入力しないでください。")


@tasks.loop(time=PM9)
async def daily_work(client: Client):
    await maintenance(client)
    await replacement_expire(client)
    await replacement(client)
    await entry_list_update(client)
    await replacement_notice_24h(client)
