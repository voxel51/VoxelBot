from hata import ClientWrapper

from ..constants import ADMIN_ROLE

ALL = ClientWrapper()


@ALL.interactions(is_global=True, show_for_invoking_user_only=True, target="user")
async def softkick(client, event, user):
    """Bans a user, then unbans them, deleting their messages in the process."""
    if not event.user.has_role(ADMIN_ROLE):
        return
    await client.guild_ban_add(
        event.guild, user, delete_message_duration=604800, reason="Softkick"
    )
    await client.guild_ban_delete(event.guild, user, reason="Softkick")
    return f"{user:f} has been softkicked."
