from datetime import datetime, timedelta, timezone

from discord import Client, Embed, File, Member

import database
from button_view import get_view

# NOTE: ビト森杯運営機能搭載ファイル
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff
JST = timezone(timedelta(hours=9))


async def search_contact(member: Member, create: bool = False, locale: str = "ja"):
    # 問い合わせチャンネル
    contact = member.guild.get_channel(database.CHANNEL_CONTACT)

    # 問い合わせスレッド一覧
    threads = contact.threads

    # スレッド名一覧 (member.id)_(locale)
    thread_names = [thread.name.split("_")[0] for thread in threads]

    # 問い合わせスレッドがすでにある場合
    if str(member.id) in thread_names:
        index = thread_names.index(str(member.id))
        return threads[index]

    # 問い合わせスレッドがなく、作成しない場合
    if create is False:
        return None

    # 問い合わせスレッドがなく、作成する場合
    thread = await contact.create_thread(name=f"{member.id}_{locale}")
    return thread


async def contact_start(client: Client, member: Member, entry_redirect: bool = False):
    # 問い合わせチャンネル
    contact = member.guild.get_channel(database.CHANNEL_CONTACT)

    # ビト森杯お知らせチャンネル
    announce = member.guild.get_channel(database.CHANNEL_BITOMORI_ANNOUNCE)

    # ビト森杯運営
    admin = member.guild.get_role(database.ROLE_ADMIN)

    tari3210 = member.guild.get_member(database.TARI3210)

    role_check = [
        member.get_role(database.ROLE_LOOP),
        member.get_role(database.ROLE_LOOP_RESERVE),
        member.get_role(database.ROLE_OLEB)
    ]
    # 最初は喋るな
    await contact.set_permissions(member, send_messages_in_threads=False)

    # 問い合わせスレッドを取得 リダイレクトならスレッド作成
    thread = await search_contact(member, create=entry_redirect)

    # スレッド名からlocaleを取得
    locale = thread.name.split("_")[1]

    # 日本語アクセスの場合
    if locale == "ja":

        # エントリー時の問い合わせリダイレクトの場合、申請内容を送信
        if entry_redirect:
            embed = await get_submission_embed(member)
            await thread.send(f"お申し込みいただき、誠にありがとうございます。\n現在の {member.mention} さんのエントリー状況は以下の通りです。", embed=embed)

        # 問い合わせの前に絵踏みさせる
        embed = Embed(
            title="お問い合わせの前に",
            description=f"イベント情報は {announce.mention} に掲載されています。\
                \n\nこれらの内容を必ずご確認ください。もし、ご質問がありましたら\n「運営に問い合わせ」ボタンを押してください。運営が対応します。",
            color=yellow
        )
        embed.set_footer(
            text=f"Make Some Noise! 開発者: {tari3210.display_name}",
            icon_url=tari3210.display_avatar.url
        )
        view = await get_view(
            call_admin=True,
            submission_content=True,
            cancel=any(role_check),  # 何かにエントリーしているならキャンセルボタンを表示
            # ビト森杯にエントリーしていないならエントリーボタンを表示
            entry_bitomori=not any([role_check[0], role_check[1]]),
            entry_exhibition=not role_check[2]  # OLEBにエントリーしていないならエントリーボタンを表示
        )
        await thread.send(f"ここは {member.mention} さん専用のお問い合わせチャンネルです。", embed=embed, view=view)

        # キャンセル待ちの場合、説明画像を送信
        if role_check[1]:
            await thread.send(
                f"### ビト森杯 キャンセル待ちについて\
                \n{member.display_name}さんはビト森杯キャンセル待ちリストに登録されています。",
                file=File("replace.jpg")
            )
        view = await get_view(info=True)
        await thread.send("以下のセレクトメニューからも詳細情報を確認できます。", view=view)

        await debug_log(
            function_name="contact_start",
            description="お問い合わせ開始",
            color=blue,
            member=member
        )
        return

    # 海外アクセスの場合
    else:
        # まず日本語での説明embedを作成
        embed_ja = Embed(
            description=f"{member.display_name}さんのDiscord言語設定が日本語ではなかったため、海外対応モードになっています。\
                \n日本語対応をご希望の場合、このチャンネルに\n\n**日本語希望**\n\nとご記入ください。\n自動で日本語対応に切り替わります。",
            color=yellow
        )
        embed_ja.set_footer(text=f"ISO 639-1 code: {locale}")
        # この時点でのlocaleは実際の言語設定

        # 各種言語の文言
        # 通常の問い合わせの場合
        langs = {
            "en-US": "Please write your inquiry here",
            "en-GB": "Please write your inquiry here",
            "zh-TW": "請把疑問寫在這裡",
            "zh-CN": "请把疑问写在这里 ※此服务器仅以日英交流",
            "ko": "문의 내용을 이 채널에 기입해주세요",
            "es-ES": "Por favor, escriba su consulta aquí",
            "pt-BR": "Por favor, escreva sua consulta aqui",
            "fr": "Veuillez écrire votre demande ici"
        }
        embed_overseas = Embed(
            title="海外からのお問い合わせ contact from overseas",
        )
        # 海外エントリー時の問い合わせリダイレクトの場合
        if entry_redirect:
            langs = {
                "en-US": "Please hold on, the moderator will be here soon",
                "en-GB": "Please hold on, the moderator will be here soon",
                "zh-TW": "請稍候片刻, 正與管理員對接",
                "zh-CN": "请稍候片刻, 正与管理员对接 ※此服务器仅以日英交流",
                "ko": "대회 운영자가 대응합니다. 잠시 기다려주십시오",
                "es-ES": "Por favor, espere un momento, el moderador estará aquí pronto",
                "pt-BR": "Por favor, aguarde um momento, o moderador estará aqui em breve",
                "fr": "Veuillez patienter, le modérateur sera bientôt là"
            }
            embed_overseas = Embed(
                title="海外からのエントリー entry from overseas",
            )
        # 言語に対応する文言を取得（ない場合英語）
        try:
            embed_overseas.description = langs[locale]
        except KeyError:
            embed_overseas.description = langs["en-US"]

        embed_overseas.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url
        )
        # 問い合わせスレッドにメンション付きで送信
        await thread.send(f"{member.mention}", embeds=[embed_overseas, embed_ja])
        await thread.send(f"{admin.mention}\n海外対応モード")

        # しゃべってよし
        await contact.set_permissions(member, send_messages_in_threads=True)

        def check(m):
            return m.channel == thread and "日本語希望" in m.content

        # 日本語希望の場合
        _ = await client.wait_for('message', check=check)

        # スレッド名を日本語モードへ変更
        await thread.edit(name=f"{member.id}_ja")
        embed = Embed(
            title="大変失礼しました",
            description="今後、日本語モードで対応いたします。",
            color=blue
        )
        # エントリー時の問い合わせリダイレクトの場合、エントリーボタンを表示
        if entry_redirect:
            embed.description += "\n\n以下のボタンからエントリーしてください。"
            view = await get_view(entry=True)
            await thread.send(member.mention, embed=embed, view=view)

        # 通常の問い合わせの場合、再度問い合わせ対応を開始
        else:
            await thread.send(member.mention, embed=embed)
            await contact_start(client, member)
        return


# TODO: 第4回ビト森杯実装（スプシ作成、そこに合わせる）
async def get_submission_embed(member: Member):
    role_check = [
        any([
            member.get_role(database.ROLE_LOOP),
            member.get_role(database.ROLE_LOOP_RESERVE)
        ]),
        any([
            member.get_role(database.ROLE_SOLO_A),
            member.get_role(database.ROLE_SOLO_A_RESERVE)
        ]),
        any([
            member.get_role(database.ROLE_SOLO_B),
            member.get_role(database.ROLE_SOLO_B_RESERVE)
        ]),
    ]
    # TODO: スプシを作る（3部門の記録をどう管理するか）
    # Google spreadsheet worksheet読み込み
    worksheet = await database.get_worksheet("エントリー名簿")

    # TODO: DBとroleの整合性チェックを行う
    # DBから取得
    cell_id = await worksheet.find(f'{member.id}')  # ユーザーIDで検索

    # そもそも何にもエントリーしていない場合
    if not any(role_check) and not bool(cell_id):
        embed_entry_status = Embed(
            title="エントリー状況照会",
            description=f"{member.display_name}さんはエントリーしていません。",
            color=yellow
        )
        return embed_entry_status

    # DB登録あり
    if any(role_check) and bool(cell_id):

        # ユーザーIDの行の値を取得
        cell_values = await worksheet.row_values(cell_id.row)
        name = cell_values[2]
        read = cell_values[3]
        status_bitomori = cell_values[4]
        status_exhibition = cell_values[5]
        device = cell_values[6].replace("\n", " ")
        note = cell_values[7].replace("\n", " ")
        time = cell_values[8]

        if status_bitomori == "":
            status_bitomori = "❌"
        if status_exhibition == "":
            status_exhibition = "❌"

        # エントリー状況照会のembedを作成
        embed_entry_status = Embed(
            title="エントリー状況照会",
            description="以下の情報が、ビト森杯データベースに記録されています。",
            color=blue
        )
        # TODO: エントリー状況を表示 (スプシに合わせる)
        for data, data_name in zip([device, note, time], ["デバイス", "備考", "エントリー日時"]):
            embed_entry_status.add_field(
                name=data_name,
                value=data
            )
        embed_entry_status.set_author(
            name=f"{name}（{read}）",
            icon_url=member.display_avatar.url
        )
        # TODO: キャンセル待ちの場合順番を表示

    # DB登録なし
    else:
        embed_entry_status = Embed(
            title="エントリー状況照会",
            description="エントリー申請は確認できましたが、情報の取得に問題が発生しました。\n\n運営が対応します。しばらくお待ちください。\n🙇ご迷惑をおかけし、申し訳ございません🙇",
            color=red
        )
        await debug_log(
            function_name="get_submission_embed",
            description="Error: DB・role同期ずれ",
            color=red,
            member=member
        )
    return embed_entry_status


async def debug_log(function_name: str, description: str, color: int, member: Member):
    # bot用チャット
    bot_channel = member.guild.get_channel(database.CHANNEL_BOT)
    tari3210 = member.guild.get_member(database.TARI3210)

    # ユーザーの問い合わせスレッドを取得
    thread = await search_contact(member)

    thread_jump_url = ""
    if bool(thread):
        thread_jump_url = "contact: " + thread.jump_url

    embed = Embed(
        title=function_name,
        description=f"{description}\n\n{member.mention}\n{thread_jump_url}\
            \n[スプレッドシート](https://docs.google.com/spreadsheets/d/1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw/edit#gid=0)",
        color=color
    )
    embed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url
    )
    embed.timestamp = datetime.now(JST)

    # エラーの場合
    if color == red:
        await bot_channel.send(f"{tari3210.mention} ERROR\n{member.id}", embed=embed)

    # それ以外の場合サイレントで送信 ユーザーに通知しない
    else:
        await bot_channel.send(f"{member.id}", embed=embed, silent=True)
    return
