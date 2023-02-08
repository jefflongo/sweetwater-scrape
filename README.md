# Sweetwater Scrape

This script scrapes [Sweetwater](https://www.sweetwater.com/) for a configurable set of product listings and posts to Discord when new items are added or sold.

To get started, modify `config.py`. 
- Set `CONFIG_PRODUCT_IDS` to a list of item IDs from Sweetwater (i.e. `LPS6ITNH`). Item IDs can be found on Sweetwater product pages.
- Set `CONFIG_DISCORD_WEBHOOK` to a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
- Optionally modify any of the other configuration options.

Install dependencies: `python -m pip install requests schedule`

To start running, simply run `python scrape.py`
