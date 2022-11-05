import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now: int = (dt.date.today().year)
    return {
        'year': year_now,
    }
