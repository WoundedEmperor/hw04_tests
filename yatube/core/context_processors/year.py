from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    today: int = datetime.today().year

    return {
        'year': today
    }
