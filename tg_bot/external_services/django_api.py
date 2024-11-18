from dataclasses import dataclass
import aiohttp
from typing import Any, Dict, Optional, List

from config_data.config import get_django_config, DjangoConfig

django_config: DjangoConfig = get_django_config()


@dataclass
class Response:
    status: int
    json: Dict[str, Any] | List[Dict[str, Any]]


async def request_django_api(
    path: str,
    method: str = 'GET',
    json_data: Optional[Dict[str, Any]] = None
) -> Response:
    async with aiohttp.ClientSession() as session:
        async with session.request(
                method=method,
                url=django_config.host_api + path,
                headers={'X-API-KEY': django_config.api_secret_key},
                json=json_data
        ) as response:
            return Response(
                status=response.status,
                json=await response.json()
            )


# ===== RECIPES =========================================================
async def get_all_recipes() -> List[Dict[str, Any]]:
    res = await request_django_api(
        path='/recipes/',
        method='GET'
    )

    return res.json


# categories
async def get_all_categories() -> List[Dict[str, Any]]:
    return (await request_django_api(
        path='/categories/',
        method='GET'
    )).json


async def get_category(category_id: int) -> Dict[str, Any]:
    return (await request_django_api(
        path=f'/categories/{category_id}/',
        method='GET'
    )).json


async def get_category_recipes(category_id: int) -> List[Dict[str, Any]]:
    return (await request_django_api(
        path=f'/categories/{category_id}/recipes/',
        method='GET'
    )).json


# ingredients
async def get_all_ingredients() -> List[Dict[str, Any]]:
    return (await request_django_api(
        path='/ingredients/',
        method='GET'
    )).json


async def get_ingredient(ingredient_id: int) -> Dict[str, Any]:
    return (await request_django_api(
        path=f'/ingredients/{ingredient_id}/',
        method='GET'
    )).json


async def get_ingredient_recipes(ingredient_id: int) -> List[Dict[str, Any]]:
    return (await request_django_api(
        path=f'/ingredients/{ingredient_id}/recipes/',
        method='GET'
    )).json


# calories ranges
async def get_calories_ranges() -> List[Dict[str, Any]]:
    return (await request_django_api(
        path='/calories_ranges/',
        method='GET'
    )).json


async def get_calories_range(calories_range_id: int) -> Dict[str, Any]:
    return (await request_django_api(
        path=f'/calories_ranges/{calories_range_id}/',
        method='GET'
    )).json


async def get_calories_range_recipes(calories_range_id: int) -> List[Dict[str, Any]]:
    return (await request_django_api(
        path=f'/calories_ranges/{calories_range_id}/recipes/',
        method='GET'
    )).json


# random recipe
async def get_random_recipe() -> Dict[str, Any]:
    return (await request_django_api(
        path='/recipes/random/',
        method='GET'
    )).json

# ===================== END RECIPES =======================================


# ===================== SELECTIONS =======================================
async def get_all_products_selections() -> List[Dict[str, Any]]:
    return (await request_django_api(
        path='/selections/',
        method='GET'
    )).json


async def get_products_selection(pk: int) -> Dict[str, Any]:
    return (await request_django_api(
        path=f'/selections/{pk}/',
        method='GET'
    )).json
# ===================== END SELECTIONS =================================


# ======================= USERS =========================================
async def get_all_users() -> List[Dict[str, Any]]:
    return (await request_django_api(
        path='/users/',
        method='GET'
    )).json


async def get_user(tg_id: int) -> Dict[str, Any]:
    return (await request_django_api(
        path=f'/users/{tg_id}/',
        method='GET'
    )).json


async def create_user(data: dict) -> Response:
    res = await request_django_api(
        path=f'/users/',
        method='POST',
        json_data=data
    )
    return res


async def get_active_users_tg_ids() -> List[int]:
    return (await request_django_api(
        path='/users/active_tg_ids/',
        method='GET'
    )).json['tg_ids']


async def unsubscribe_user(tg_id: int) -> Response:
    return (await request_django_api(
        path=f'/users/{tg_id}/unsubscribe/',
        method='PATCH'
    ))


async def get_users_stats() -> Dict[str, int]:
    return (await request_django_api(
        path='/users/stats/',
        method='GET'
    )).json


# ===================== SERVICE========================
async def db_backup() -> Response:
    return await request_django_api(
        path='/service/backup/',
        method='POST'
    )
