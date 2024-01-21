from datetime import datetime, timedelta, timezone

from discord import Message

JST = timezone(timedelta(hours=9))


async def countdown():

    # GBB開始日時
    # 2024/11/1 0:00
    dt_gbb_start = datetime(2024, 11, 1, 0, 0)

    # GBB終了日時
    # 2024/11/4 0:00
    dt_gbb_end = datetime(2024, 11, 4)

    dt_gbb_start = dt_gbb_start.replace(tzinfo=JST)  # JSTに変換
    dt_gbb_end = dt_gbb_end.replace(tzinfo=JST)  # JSTに変換
    dt_now = datetime.now(JST)

    td_gbb = abs(dt_gbb_end - dt_now)  # GBB終了から現在の時間
    if dt_gbb_end > dt_now:  # GBB終了前なら
        td_gbb = abs(dt_gbb_start - dt_now)  # GBB開始から現在の時間

    m, s = divmod(td_gbb.seconds, 60)  # 秒を60で割った商と余りをm, sに代入
    h, m = divmod(m, 60)  # mを60で割った商と余りをh, mに代入

    if dt_gbb_start > dt_now:  # GBB開始前なら
        return f"GBB{dt_gbb_start.year}まであと{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒です。"

    elif dt_gbb_end > dt_now:  # GBB開催中なら
        return f"今日はGBB{dt_gbb_start.year} {td_gbb.days + 1}日目です。"

    # GBB終了後なら
    return f"GBB{dt_gbb_start.year}は{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒前に開催されました。"


async def send_gbbinfo(message: Message):

    # ジャッジ一覧
    if "judge" in message.content:
        url = "https://gbbinfo-jpn.jimdofree.com/20240121/#p06"  # ジャッジ一覧のURL
        await message.channel.send(f"[GBBジャッジ一覧はこちら]({url})")
        return

    # Wildcard結果
    if "wc" in message.content:
        url = ""  # Wildcard結果のURL
        await message.channel.send(f"[GBB Wildcard結果はこちら]({url})")
        return

    # Wildcardルール
    if "rule" in message.content:
        url = "https://gbbinfo-jpn.jimdofree.com/20240121/"  # WildcardルールのURL
        await message.channel.send(f"[GBB Wildcardルールはこちら]({url})")
        return
