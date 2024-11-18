

from aiogram.filters import BaseFilter
from aiogram.types import Update


# SIGN UP FORM FILTERS
class IsAdmin(BaseFilter):
    async def __call__(self, update: Update, admin_ids: list[int]) -> bool:
        return update.from_user.id in admin_ids






