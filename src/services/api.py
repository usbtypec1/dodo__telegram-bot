import contextlib
import json
import uuid
from typing import Iterable, Sequence, TypeVar, Type, Generic, AsyncGenerator

import httpx
from pydantic import parse_obj_as

import models
from config import app_settings
from utils import exceptions

RM = TypeVar('RM')


async def request_to_api(
        url: str,
        method: str,
        params: dict | None = None,
        body: dict | None = None,
) -> list | dict:
    async with httpx.AsyncClient(base_url=app_settings.api_url) as client:
        try:
            response = await client.request(method=method, url=url, params=params, json=body, timeout=30)
            return response.json()
        except (httpx.HTTPError, json.JSONDecodeError):
            raise exceptions.DodoAPIError


class RequestByCookiesAndUnitIds(Generic[RM]):

    def __init__(self, url: str, response_model: Type[RM]):
        self._response_model = response_model
        self._url = url

    async def request(self, cookies: dict, unit_ids: Iterable[int]) -> RM:
        body = {'cookies': cookies, 'unit_ids': unit_ids}
        response_json = await request_to_api(self._url, method='POST', body=body)
        return self._response_model.parse_obj(response_json)

    def __call__(self, cookies: dict, unit_ids: Iterable[int]):
        return self.request(cookies, unit_ids)


get_kitchen_performance_statistics = RequestByCookiesAndUnitIds(
    url='/v1/statistics/kitchen/performance',
    response_model=models.KitchenPerformanceStatistics,
)

get_kitchen_production_statistics = RequestByCookiesAndUnitIds(
    url='/v1/statistics/production/kitchen',
    response_model=models.KitchenProductionStatistics,
)

get_delivery_performance_statistics = RequestByCookiesAndUnitIds(
    url='/v1/statistics/delivery/performance',
    response_model=models.DeliveryPerformanceStatistics,
)

get_heated_shelf_statistics = RequestByCookiesAndUnitIds(
    url='/v1/statistics/delivery/heated-shelf',
    response_model=models.HeatedShelfStatistics,
)

get_couriers_statistics = RequestByCookiesAndUnitIds(
    url='/v1/statistics/delivery/couriers',
    response_model=models.CouriersStatistics,
)


async def get_revenue_statistics(
        unit_ids: Iterable[int] | Sequence[int],
) -> models.RevenueStatistics:
    url = '/v1/statistics/revenue'
    params = {'unit_ids': tuple(unit_ids)}
    response_json = await request_to_api(url, method='GET', params=params)
    return models.RevenueStatistics.parse_obj(response_json)


async def get_being_late_certificates_statistics(
        cookies: dict,
        unit_ids_and_names: Iterable[models.UnitIdAndName],
) -> list[models.UnitBeingLateCertificatesTodayAndWeekBefore]:
    url = '/v1/statistics/being-late-certificates'
    body = {'cookies': cookies, 'units': tuple(unit_ids_and_names)}
    response_json = await request_to_api(url, method='POST', body=body)
    return parse_obj_as(list[models.UnitBeingLateCertificatesTodayAndWeekBefore], response_json)


async def get_bonus_system_statistics(
        cookies: dict,
        unit_ids_and_names: Iterable[models.UnitIdAndName],
) -> list[models.UnitBonusSystem]:
    url = '/v1/statistics/bonus-system'
    body = {'cookies': cookies, 'units': tuple(unit_ids_and_names)}
    response_json = await request_to_api(url, method='POST', body=body)
    return parse_obj_as(list[models.UnitBonusSystem], response_json)


async def get_delivery_speed_statistics(
        token: str,
        unit_uuids: Iterable[uuid.UUID],
) -> list[models.UnitDeliverySpeed]:
    url = '/v2/statistics/delivery/speed'
    params = {'token': token, 'unit_uuids': [unit_uuid.hex for unit_uuid in unit_uuids]}
    response_json = await request_to_api(url, method='GET', params=params)
    return parse_obj_as(list[models.UnitDeliverySpeed], response_json)


async def get_orders_handover_time_statistics(
        token: str,
        unit_uuids: Iterable[uuid.UUID],
) -> list[models.UnitOrdersHandoverTime]:
    url = '/v2/statistics/production/handover-time'
    params = {'token': token, 'unit_uuids': [unit_uuid.hex for unit_uuid in unit_uuids],
              'sales_channels': [models.SalesChannel.DINE_IN.value]}
    response_json = await request_to_api(url, method='GET', params=params)
    return parse_obj_as(list[models.UnitOrdersHandoverTime], response_json)


@contextlib.asynccontextmanager
async def async_client(base_url: str = '') -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=base_url) as client:
        yield client


async def get_access_token(client: httpx.AsyncClient, account_name: str) -> models.AccessToken:
    response = await client.get('/auth/token/', params={'account_name': account_name})
    if response.is_success:
        return response.json()['access_token']
    if response.status_code == 404:
        raise exceptions.NoTokenError
    else:
        raise exceptions.DatabaseAPIError


async def get_cookies(client: httpx.AsyncClient, account_name: str) -> models.Cookies:
    response = await client.get('/auth/cookies/', params={'account_name': account_name})
    if response.is_success:
        return response.json()
    if response.status_code == 404:
        raise exceptions.NoCookiesError
    else:
        raise exceptions.DatabaseAPIError
