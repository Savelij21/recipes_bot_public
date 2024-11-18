
from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


# all other updates
@router.message()
@router.edited_message()
@router.channel_post()
@router.edited_channel_post()
@router.inline_query()
@router.chosen_inline_result()
@router.callback_query()
@router.shipping_query()
@router.pre_checkout_query()
@router.poll()
@router.poll_answer()
@router.my_chat_member()
@router.chat_member()
@router.chat_join_request()
@router.message_reaction()
@router.message_reaction_count()
@router.chat_boost()
@router.removed_chat_boost()
# @router.deleted_business_messages()
# @router.business_connection()
# @router.edited_business_message()
# @router.business_message
async def process_other_updates(update: CallbackQuery | Message) -> None:
    # dev
    if isinstance(update, (CallbackQuery, Message)):
        await update.answer('O_o')
    else:
        pass
    return





