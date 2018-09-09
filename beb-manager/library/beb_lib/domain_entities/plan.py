import datetime


class Plan:
    """
    Class that is used to create task from template according to interval
    """

    def __init__(self,
                 interval: datetime.timedelta,
                 card_id: int,
                 last_created_at: datetime.datetime,
                 unique_id: int=None):
        self.unique_id = unique_id
        self.card_id = card_id
        self.interval = interval
        self.last_created_at = last_created_at
