from src.redis.config import Redis
import asyncio
from src.model.gptj import GPT
from src.redis.cache import Cache
from src.schema.chat import Message

redis = Redis()


async def main():
    json_client = redis.create_rejson_connection()

    await Cache(json_client).add_message_to_cache(token="4299457f-c453-44db-bcf1-dbafe6880ba5",
                                                  source="human",
                                                  message_data={
                                                      "id": "5",
                                                      "msg": "What's your favorite hobby?",
                                                      "timestamp": "2023-02-22 01:08:59.530218"
                                                  })

    data = await Cache(json_client).get_chat_history(token="4299457f-c453-44db-bcf1-dbafe6880ba5")

    print(data)

    message_data = data['messages'][-4:]
    input = ["" + i['msg'] for i in message_data]
    input = " ".join(input)

    res = GPT().query(input=input)

    msg = Message(
        msg=res
    )

    print(msg)
    await Cache(json_client).add_message_to_cache(token="4299457f-c453-44db-bcf1-dbafe6880ba5",
                                                  source="bot",
                                                  message_data=msg.dict())


if __name__ == "__main__":
    asyncio.run(main())
