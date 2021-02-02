import math
from datetime import date, timedelta

import workdays

from back_office.models import PacketItem


def hours_to_date(hours, working_day=8):
    """возввращает количество рабочих дней (working_day - количество часов в рабочем дне)"""
    days = hours / working_day
    return math.ceil(days)


def get_statement_date_meeting(sailor_key=None, hour_for_statement=None, working_day=8):
    """Возвращает дату для обращения моряка в учреждение по его заялвению"""
    today = date.today()
    packet_after_today = PacketItem.by_sailor.filter_by_sailor(sailor_key=sailor_key, date_end_meeting__gt=today)
    if packet_after_today.exists():
        date_start = packet_after_today.order_by('date_end_meeting').last().date_end_meeting
    else:
        date_start = today
    last_date = date_start + timedelta(days=1)
    if last_date.isoweekday() in [6, 7]:
        last_date += timedelta(days=8 - last_date.isoweekday())
    date_end_meeting = None
    if hour_for_statement is not None:
        quantity_work_days = hours_to_date(hour_for_statement, working_day)
        date_end_meeting = workdays.workday(last_date, quantity_work_days)
    return {'date_meeting': last_date, 'date_end_meeting': date_end_meeting}