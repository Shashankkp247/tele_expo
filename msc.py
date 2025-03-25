from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = "24643092"
api_hash = "d650419e556eb237e53969c4bfa6d480"
channel_username = -1002341119224

client = TelegramClient("session", api_id, api_hash)

async def count_messages():
    async with client:
        history = await client(GetHistoryRequest(
            peer=channel_username,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=1,  # We only need one message to get total count
            max_id=0,
            min_id=0,
            hash=0
        ))

        total_count = history.count
        print(f"Total messages in {channel_username}: {total_count}")

client.start()
client.loop.run_until_complete(count_messages())
client.disconnect()
