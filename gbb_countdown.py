from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


async def gbb_countdown():
    dt_gbb_start = datetime(2023, 10, 18, 13, 0)  # 2023/10/18 13:00
    dt_gbb_end = datetime(2023, 10, 22)  # 2023/10/22
    dt_gbb_start = dt_gbb_start.replace(tzinfo=JST)  # JSTに変換
    dt_gbb_end = dt_gbb_end.replace(tzinfo=JST)  # JSTに変換
    dt_now = datetime.now(JST)

    td_gbb = abs(dt_gbb_end - dt_now)  # GBB終了から現在の時間
    if dt_gbb_end > dt_now:  # GBB終了前なら
        td_gbb = abs(dt_gbb_start - dt_now)  # GBB開始から現在の時間

    m, s = divmod(td_gbb.seconds, 60)  # 秒を60で割った商と余りをm, sに代入
    h, m = divmod(m, 60)  # mを60で割った商と余りをh, mに代入

    if dt_gbb_start > dt_now:  # GBB開始前なら
        return f"GBB2023まであと{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒です。"

    elif dt_gbb_end > dt_now:  # GBB開催中なら
        return f"今日はGBB2023 {td_gbb.days + 1}日目です。"

    # GBB終了後なら
    return f"GBB2023は{td_gbb.days}日{h}時間{m}分{s}.{td_gbb.microseconds}秒前に開催されました。"
