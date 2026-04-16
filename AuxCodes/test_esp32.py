import time
from is_wire.core import Subscription, Message, Logger
from streamChannel import StreamChannel

broker_uri = "amqp://guest:guest@10.10.2.211:30000"
local_channel = StreamChannel(broker_uri)

time.sleep(5)
# while True:
msg_text = str(1)
print(msg_text)
img_msg = Message()
img_msg.body = msg_text.encode("utf-8")
local_channel.publish(img_msg, topic='result')
