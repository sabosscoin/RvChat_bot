import os
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
import openai

# Get API credentials from environment variables
API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
PHONE_NUMBER = os.environ['PHONE_NUMBER']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
TELEGRAM_SESSION_STRING = os.environ['TELEGRAM_SESSION_STRING']

openai.api_key = OPENAI_API_KEY
client = TelegramClient(StringSession(TELEGRAM_SESSION_STRING), API_ID, API_HASH)

async def generate_response(conversation_history):
    me = await client.get_me()

    prompt = []

    #loop through the conversation history
    for message in reversed(conversation_history):
        if message.sender == me: #from bot
            prompt.append({"role": "assistant", "content": message.text})
        else:
            prompt.append({"role": "user", "content": message.text})


    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=prompt
    )

    reply_text = response.choices[0].message.content.strip()
    return reply_text

async def get_last_x_messages(client, channel_id, limit):
    # Get the channel entity
    channel = await client.get_entity(channel_id)

    # Fetch the last `limit` messages from the channel
    messages = await client.get_messages(channel, limit=limit)

    return messages

async def on_new_message(event):
    if event.chat_id != 88834504:
        # For now debug only on my account
        return

    async with client.action(event.chat_id, 'typing'):
        conversation_history = await get_last_x_messages(client, event.chat_id, 20)
        response = await generate_response(conversation_history)

    await client.send_message(event.chat_id, response)

async def main():
    # Initialize the Telegram client
    # Connect and sign in using the phone number

    await client.start()

    client.add_event_handler(on_new_message, events.NewMessage)

    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())