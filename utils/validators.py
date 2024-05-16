import json

from datetime import datetime

from utils import exceptions as e


class Validators:

    GROUPS = ('hour', 'day', 'month')
    EXCEPTIONS = (
        SyntaxError,
        NameError,
        TypeError,
        ValueError,
        OverflowError,
        MemoryError
    )

    def validate_json(self, request: str) -> None:
        try:
            json.dumps(eval(request))
        except self.EXCEPTIONS:
            raise e.WrongInputFormat

    def validate_group_type(self, group_type: str | None) -> None:
        if group_type not in self.GROUPS:
            raise e.WrongGroupType

    def validate_time_format(self, time: str) -> None:
        try:
            datetime.fromisoformat(time)
        except self.EXCEPTIONS:
            raise e.WrongTimeFormat

    def validate_request(self, request: str) -> None:
        self.validate_json(request)
        data: dict = eval(request)
        self.validate_group_type(data.get('group_type'))
        self.validate_time_format(data.get('dt_from'))
        self.validate_time_format(data.get('dt_upto'))
