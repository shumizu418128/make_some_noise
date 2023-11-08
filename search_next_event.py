from discord import EventStatus, ScheduledEvent


async def search_next_event(events: list[ScheduledEvent]):
    events_exist = []  # 予定されているイベント
    for event in events:  # 予定されているイベントをリストに追加
        if event.status in [EventStatus.scheduled, EventStatus.active]:
            events_exist.append(event)
    if bool(events_exist) is False:  # 予定されているイベントがない場合さよなら
        return None
    closest_event = events_exist[0]
    for event in events_exist:  # 一番近いイベントを探す
        if event.start_time < closest_event.start_time:
            closest_event = event
    return closest_event
