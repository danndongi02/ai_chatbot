from src.redis.config import Redis
import asyncio
from src.model.gptj import GPT
from src.redis.cache import Cache
from src.schema.chat import Message
import os
from dotenv import load_dotenv
from src.redis.stream import StreamConsumer
from src.redis.producer import Producer

redis = Redis()
load_dotenv()


async def main():
    json_client = redis.create_rejson_connection()
    redis_client = await redis.create_connection()
    consumer = StreamConsumer(redis_client)
    cache = Cache(json_client)

    print("Stream consumer started")
    print("Stream waiting for new messages")

    while True:
        response = await consumer.consume_stream(stream_channel="message_channel", count=1, block=0)

        if response:
            for stream, messages in response:
                # Get the message from stream, and extract token, message data and message id
                for message in messages:
                    message_id = message[0]
                    token = [k.decode('utf-8')
                             for k, v in message[1].items()][0]
                    message = [v.decode('utf-8')
                               for k, v in message[1].items()][0]
                    print(token)

                    # Create a new message instance and add to cache
                    # specify the source as human
                    msg = Message(msg=message)

                    await Cache.add_message_to_cache(token=token, source="human", message_data=msg.dict())

                    # get chat history from cache
                    data = await cache.get_chat_history(token=token)

                    # clean message input and send query
                    message_data = data['messages'][-4]

                    message_data = data['messages'][-4:]
                    _input = ["" + i['msg'] for i in message_data]
                    _input = " ".join(_input)

                    res = GPT().query(input=_input)

                    msg = Message(
                        msg=res  # type: ignore
                    )

                    stream_data = {}
                    stream_data[str(token)] = str(msg.dict())

                    await Producer.add_to_stream(stream_data, "response channel")


                    await cache.add_message_to_cache(token=token, source="bot", message_data=msg.dict())

                # Delete message from queue after it has been processed
                await consumer.delete_message(stream_channel="message_channel", message_id=message_id)


if __name__ == "__main__":
    asyncio.run(main())
