from src.redis.config import Redis
import asyncio
from src.model.gptj import GPT
from src.redis.cache import Cache
from src.schema.chat import Message
import os
from dotenv import load_dotenv

redis = Redis()
load_dotenv()


async def main():
    json_client = redis.create_rejson_connection()

    await Cache(json_client).add_message_to_cache(token=os.environ['TEST_USER_TOKEN'],
                                                  source="human",
                                                  message_data={
                                                      "id": "2",
                                                      "msg": "What's cooking?",
                                                      "timestamp": "2023-02-22 01:08:59.530218"
    })

    data = await Cache(json_client).get_chat_history(token=os.environ['TEST_USER_TOKEN'])

    print(data)

    message_data = data['messages'][-4:]
    _input = ["" + i['msg'] for i in message_data]
    _input = " ".join(_input)

    res = GPT().query(input=_input)

    msg = Message(
        msg=res # type: ignore
    )

    print(msg)
    await Cache(json_client).add_message_to_cache(token=os.environ['TEST_USER_TOKEN'],
                                                  source="bot",
                                                  message_data=msg.dict())


if __name__ == "__main__":
    asyncio.run(main())
