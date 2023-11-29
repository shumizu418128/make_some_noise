from datetime import timedelta, timezone

from discord import Client, Embed, Member
from oauth2client.service_account import ServiceAccountCredentials

from button_view import get_view

# NOTE: ビト森杯運営機能搭載ファイル
green = 0x00ff00
yellow = 0xffff00
red = 0xff0000
blue = 0x00bfff
JST = timezone(timedelta(hours=9))

"""
Google spreadsheet
row = 縦 1, 2, 3, ...
col = 横 A, B, C, ...
"""


def get_credits():
    return ServiceAccountCredentials.from_json_keyfile_name(
        "makesomenoise-4cb78ac4f8b5.json",
        ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets'])


async def search_contact(member: Member, create: bool = False, locale: str = "ja"):
    contact = member.guild.get_channel(
        1035964918198960128  # 問い合わせ
    )
    threads = contact.threads  # 問い合わせスレッド一覧
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


# TODO: 動作テスト
async def contact_start(client: Client, member: Member, entry_redirect: bool = False):
    # 問い合わせスレッドを取得 リダイレクトならスレッド作成
    thread = await search_contact(member, create=entry_redirect)
    contact = thread.guild.get_channel(
        1035964918198960128  # 問い合わせ
    )
    announce = thread.guild.get_channel(
        1035965200341401600  # ビト森杯お知らせ
    )
    admin = thread.guild.get_role(
        904368977092964352  # ビト森杯運営
    )
    locale = thread.name.split("_")[1]  # スレッド名からlocaleを取得
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

    # 最初は喋るな
    await contact.set_permissions(member, send_messages_in_threads=False)

    # 日本語アクセスの場合
    if locale == "ja":
        embed = Embed(
            title="お問い合わせの前に",
            description=f"ビト森杯の情報は\n{announce.mention}\nに掲載されています。\
                \n\nこれらの内容を必ずご確認ください。もし、ご質問がありましたら\n「ビト森杯運営に問い合わせ」ボタンを押してください。運営が対応します。",
            color=yellow
        )
        view = await get_view(
            call_admin=True,
            submission_content=True,
            cancel=any(role_check),  # 何かにエントリーしているならキャンセルボタンを表示
            entry=not any(role_check)  # 何もエントリーしていないならエントリーボタンを表示
        )
        await thread.send(f"ここは {member.mention} さん専用のお問い合わせチャンネルです。", embed=embed, view=view)
        return

    # 海外アクセスの場合
    else:
        available_langs = [
            "ko", "zh-TW", "zh-CN",
            "en-US", "en-GB", "es-ES", "pt-BR"
        ]
        if locale not in available_langs:
            locale = "en-US"
        lang_contact = {
            "en-US": "Please write your inquiry here",
            "en-GB": "Please write your inquiry here",
            "zh-TW": "請把疑問寫在這裡",
            "zh-CN": "请把疑问写在这里 ※此服务器仅以日英交流",
            "ko": "문의 내용을 이 채널에 기입해주세요",
            "es-ES": "Por favor, escriba su consulta aquí",
            "pt-BR": "Por favor, escreva sua consulta aqui"
        }
        lang_entry_redirect = {
            "en-US": "Please hold on, the moderator will be here soon",
            "en-GB": "Please hold on, the moderator will be here soon",
            "zh-TW": "請稍候片刻, 正與管理員對接",
            "zh-CN": "请稍候片刻, 正与管理员对接 ※此服务器仅以日英交流",
            "ko": "대회 운영자가 대응합니다. 잠시 기다려주십시오",
            "es-ES": "Por favor, espere un momento, el moderador estará aquí pronto",
            "pt-BR": "Por favor, aguarde um momento, o moderador estará aqui em breve"
        }
        embed_overseas = Embed(  # 通常の問い合わせ
            title="海外からのお問い合わせ contact from overseas",
            description=lang_contact[locale],
            color=blue
        )
        if entry_redirect:  # 海外エントリー時の問い合わせリダイレクトの場合
            embed_overseas = Embed(
                title="海外からのエントリー entry from overseas",
                description=lang_entry_redirect[locale],
                color=blue
            )
        embed_ja = Embed(
            description=f"{member.display_name}さんのDiscord言語設定が日本語ではなかったため、海外対応モードになっています。\
                \n日本語対応をご希望の場合、このチャンネルに\n\n**日本語希望**\n\nとご記入ください。\n自動で日本語対応に切り替わります。"
        )
        embed_ja.set_footer(text=f"ISO 639-1 code: {locale}")

        # 問い合わせスレッドにメンション付きで送信
        await thread.send(f"{member.mention}", embeds=[embed_overseas, embed_ja])
        await thread.send(f"{admin.mention}\n海外対応モード")

        # しゃべってよし
        await contact.set_permissions(member, send_messages_in_threads=True)

        def check(m):
            return m.channel == thread and m.content == "日本語希望"

        _ = await client.wait_for('message', check=check)

        """
        日本語モードへ変更
        """

        # スレッド名を日本語モードへ変更
        await thread.edit(name=f"{member.id}_ja")
        embed = Embed(
            title="大変失礼しました",
            description="今後、日本語モードで対応いたします。",
            color=blue)

        # エントリー時の問い合わせリダイレクトの場合
        if entry_redirect:
            embed.description += "\n\n以下のボタンからエントリーしてください。"
            view = await get_view(entry=True)
            await thread.send(member.mention, embed=embed, view=view)

        # 通常の問い合わせ
        else:
            await thread.send(member.mention, embed=embed)
            await contact_start(client, member)
        return
