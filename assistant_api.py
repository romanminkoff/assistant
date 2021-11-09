import pika

PIKA_QUEUE = "assistant"
PIKA_HOST = "localhost"

def send_message(json_obj):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=PIKA_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=PIKA_QUEUE)

    channel.basic_publish(exchange='', routing_key=PIKA_QUEUE, 
        body=json_obj)
    connection.close()

def receiver(callback):
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=PIKA_HOST))
    channel = conn.channel()
    channel.queue_declare(queue=PIKA_QUEUE)

    def _callback(ch, method, properties, body):
        callback(body)

    channel.basic_consume(queue=PIKA_QUEUE, on_message_callback=_callback,
        auto_ack=True)
    channel.start_consuming()