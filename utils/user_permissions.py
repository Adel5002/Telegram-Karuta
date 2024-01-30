from db_settings.db_models import Player


def user_is_verified(player: Player) -> bool:
    if player is not None and player.is_verified:
        return True
    else:
        return False

