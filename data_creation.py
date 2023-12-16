from confluent_kafka import Producer
import logging
import random
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def create_power_random_data():
    return {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "l1": random.randint(230, 245),
        "l2": random.randint(230, 245),
        "l3": random.randint(230, 245),
    }


def kafka_producer_power(
    kafka_topic: str = "power.power_data",
    kafka_brokers: str = "localhost:9093",
    request_dict: dict = create_power_random_data(),
):
    p = Producer(
        {
            # For more info on these settings, see:
            # https://kafka.apache.org/documentation/#producerconfigs
            # use a comma seperated str to add multiple brokers
            "bootstrap.servers": kafka_brokers,
            "socket.keepalive.enable": True,
        }
    )

    p.produce(kafka_topic, str(request_dict))
    p.poll(1)
    p.flush()
    logger.info(f"Sent message: {request_dict}")
    return request_dict


def kafka_consumer_power(
    kafka_topic: str = "power.power_data",
    kafka_brokers: str = "localhost:9093",
):
    from confluent_kafka import Consumer

    c = Consumer(
        {
            # For more info on these settings, see:
            # https://kafka.apache.org/documentation/#consumerconfigs
            # use a comma seperated str to add multiple brokers
            "bootstrap.servers": kafka_brokers,
            "group.id": "power",
            "auto.offset.reset": "earliest",
            "socket.keepalive.enable": True,
        }
    )
    c.subscribe([kafka_topic])
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue
        logger.info(f"Received message: {msg.value().decode('utf-8')}")
        return msg.value().decode("utf-8")
    # c.close()
