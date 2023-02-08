# Sweetwater product IDs
CONFIG_PRODUCT_IDS: list = []  # TODO: populate

# Discord channel webhook URL
CONFIG_DISCORD_WEBHOOK: str = ""  # TODO: populate

# Discord roles to ping on new listing
CONFIG_DISCORD_PING_ROLES: list = ["everyone"]

# How often to check for listing updates
CONFIG_REFRESH_RATE_SECONDS: int = 5 * 60

# Post a discord message once a day notifying that the service is still
CONFIG_POST_HEARTBEAT: bool = True
