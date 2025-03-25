import asyncio
from telethon.sync import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from tqdm import tqdm

# 🔹 Enter your API credentials (Get from https://my.telegram.org/apps)
api_id = "24643092"
api_hash = "d650419e556eb237e53969c4bfa6d480"
source_channel = -1002341119224  # Example: "@example_channel"
destination_channel = -1002515340484

client = TelegramClient("session", api_id, api_hash)

async def ensure_connection():
    """Ensures the client is connected before making API requests."""
    if not client.is_connected():
        print("Reconnecting to Telegram...")
        await client.connect()
        if not client.is_user_authorized():
            print("Session expired! Please log in again.")
            await client.send_code_request("YOUR_PHONE_NUMBER")  # Replace with your phone
            code = input("Enter the login code: ")
            await client.sign_in("YOUR_PHONE_NUMBER", code)
        print("Reconnected successfully!")

async def count_messages():
    """Counts the total number of messages in the source channel."""
    await ensure_connection()
    history = await client(GetHistoryRequest(
        peer=source_channel,
        offset_id=0,
        offset_date=None,
        add_offset=0,
        limit=1,  # Just fetch 1 message to get total count
        max_id=0,
        min_id=0,
        hash=0
    ))
    return history.count

async def forward_messages():
    """Fetches and forwards all messages from source to destination in the correct order."""
    await ensure_connection()

    total_count = await count_messages()
    print(f"Total messages in {source_channel}: {total_count}")

    # Fetch all messages
    all_messages = []
    offset_id = 0
    while True:
        await ensure_connection()
        try:
            history = await client(GetHistoryRequest(
                peer=source_channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=100,  # Fetch messages in batches
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            all_messages.extend(history.messages)
            offset_id = history.messages[-1].id  # Move to the next batch
        except Exception as e:
            print(f"Error fetching messages: {e}")
            await asyncio.sleep(5)  # Wait before retrying

    # Reverse messages to maintain original order (top to bottom)
    all_messages.reverse()

    # Progress bar to track forwarding
    with tqdm(total=len(all_messages), desc="Forwarding Messages") as pbar:
        for message in all_messages:
            await ensure_connection()
            try:
                await client.send_message(destination_channel, message)
                await asyncio.sleep(1)  # 🔹 Delay to prevent rate limits
                pbar.update(1)
            except Exception as e:
                print(f"Error forwarding message: {e}")
                await asyncio.sleep(5)  # Retry delay if an error occurs

@client.on(events.NewMessage(chats=source_channel))
async def forward_new_message(event):
    """Forwards new messages in real-time as they arrive."""
    await ensure_connection()
    try:
        await client.send_message(destination_channel, event.message)
    except Exception as e:
        print(f"Error forwarding new message: {e}")
        await asyncio.sleep(5)  # Retry delay if an error occurs

print("Bot is starting...")

client.start()
client.loop.run_until_complete(forward_messages())  # Forward old messages
client.run_until_disconnected()  # Keep listening for new messages
