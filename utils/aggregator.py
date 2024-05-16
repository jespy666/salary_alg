from datetime import datetime, timedelta

from db.mongo_manager import AsyncMongoManager

from utils.validators import Validators

from config import mongo_config


class SalaryAggregator(Validators, AsyncMongoManager):

    def __init__(self, request: str) -> None:
        super().__init__(config=mongo_config)
        # validate user input
        super().validate_request(request)
        self.request = eval(request)
        self.group_type = self.request.get('group_type')
        self.dt_from = datetime.fromisoformat(self.request['dt_from'])
        self.dt_upto = datetime.fromisoformat(self.request['dt_upto'])

    def get_group_filter(self) -> dict:
        # checkout the group type and set equal filter
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
        # Get labels for 'day' and 'hour' group cases.
        # It is assumed that there will be at least one payment per month
        # For other cases, a template is created that consists
        # of continuous intervals
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
        # convert time format to ISO
        return list(map(lambda x: x.isoformat(), labels))

    async def get_response(self) -> dict:
        # Get data from db by prepared pipeline
        data: list = await self.fetch_data()
        # Get interval template
        labels: list | None = self.get_labels()
        # If there is no template, assume that this is a grouping by month
        if not labels:
            # So we equate the labels with the data received from the database
            labels = [date['_id'] for date in data]
        data_dates = {date['_id']: date['total_value'] for date in data}
        # Generate dataset with zeros for days without payments
        dataset = [data_dates.get(label, 0) for label in labels]
        return {'dataset': dataset, 'labels': self.set_iso(labels)}
