import calendar

from datetime import datetime, timedelta

from db.mongo_manager import AsyncMongoManager

from utils.validators import Validators

from config import mongo_config


class SalaryAggregator(Validators, AsyncMongoManager):

    def __init__(self, request: str) -> None:
        super().__init__(config=mongo_config)
        super().validate_request(request)
        self.request = eval(request)
        self.group_type = self.request.get('group_type')
        self.dt_from = datetime.fromisoformat(self.request['dt_from'])
        self.dt_upto = datetime.fromisoformat(self.request['dt_upto'])

    def get_group_filter(self) -> dict:
        date_parts = {
            "year": {"$year": "$dt"},
            "month": {"$month": "$dt"},
            "day": {"$dayOfMonth": "$dt"} if self.group_type in ['day', 'hour']
            else None,
            "hour": {"$hour": "$dt"} if self.group_type == 'hour' else None
        }
        group_filter = {
            "$group": {
                "_id": {
                    "$dateFromParts": {
                        k: v for k, v in date_parts.items() if v
                    }
                },
                "total_value": {"$sum": "$value"}
            }
        }
        return group_filter

    async def fetch_data(self) -> list:

        pipeline = [
            {"$match": {"dt": {"$gte": self.dt_from, "$lte": self.dt_upto}}},
            self.get_group_filter(),
            {"$sort": {"_id": 1}},
        ]
        return await super().aggregate(pipeline)

    def get_labels(self) -> list:
        match self.group_type:
            case g if g == 'day':
                return [self.dt_from + timedelta(days=i)
                        for i in range((self.dt_upto - self.dt_from).days + 1)]
            case g if g == 'hour':
                diff = (self.dt_upto - self.dt_from).total_seconds() // 3600
                return [self.dt_from + timedelta(hours=i)
                        for i in range(int(diff))]

    @staticmethod
    def set_iso(labels: list) -> list:
        return list(map(lambda x: x.isoformat(), labels))

    async def get_response(self) -> dict:
        data: list = await self.fetch_data()
        labels: list | None = self.get_labels()
        if not labels:
            labels = [date['_id'] for date in data]
        diff: int = len(labels) - len(data)
        sum_list: list = [i['total_value'] for i in data]
        if diff > 0:
            dataset = [0] * diff + sum_list
        else:
            dataset = sum_list
        return {'dataset': dataset, 'labels': self.set_iso(labels)}
