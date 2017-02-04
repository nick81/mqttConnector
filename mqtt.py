import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, rc):
#     print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	# client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
# 	print(msg.topic+" "+str(msg.payload))

class Subscription:
    def __init__(self,topic, cb):
        self.topic = topic
        self.cb = cb

class Mqtt(object):
    """docstring for Mqtt."""
    subscriptions = []
    client = None
    userdata = None
    rc = None
    __client = mqtt.Client()
    __mqttServer = 'iot.mybergmann.net'
    __mqttUsername = 'nick'
    __mqttPassword = 'sandra'
    __mqttPort = 8883

    def __init__(self, topic, cb):
        super(Mqtt, self).__init__()
        self.topic = topic
        self.cb = cb
        self.subscribe(topic,cb)
    def subscribe(self,topic,cb):
        sub = Subscription(topic,cb)
        if len(self.subscriptions) == 0:
            self.__connect()
        print('Subscribe')
        self.subscriptions.append(sub)
    def unsubscribe(self):
        print('unsubscribe')
        # pass
    def publish(self, payload, topic = None):
        print('Publish')
        if topic == None:
            topic = self.topic
        print(topic, payload)
        self.__client.publish(topic, payload, retain=True)
        # self.on_message(None, None, None, "hallo")
    @classmethod
    def __connect(self):
        print('Connect')
        self.__client.username_pw_set(self.__mqttUsername, self.__mqttPassword)
        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message
        self.__client.connect_async(self.__mqttServer, self.__mqttPort, 60)
        self.__client.loop_start()
        # self.__client.loop_forever()
    def __disconnect(self):
        self.__client.disconnect()
    @classmethod
    def on_message(self, client, userdata, msg):
        print('Message reseived')
        # print(msg)
        calls = filter(lambda x: x.topic.startswith(msg.topic), self.subscriptions)
        for call in calls:
            call.cb(msg)
    @classmethod
    def on_connect(self, client, userdata, rc, arg):
        print('Connected')
        print(client, userdata, rc)
        for sub in self.subscriptions:
            self.__client.message_callback_add(sub.topic,sub.cb)
            print('Subscribe:',sub.topic)
            # self.__client.subscribe(sub.topic)
        self.client = client
        self.userdata = userdata
        self.rc = rc
    @classmethod
    def on_disconnect(self, client, userdata, rc):
        print('Disconnected')
        self.client = None
        self.userdata = None
        self.rc = None

class Msg:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

def i1func(msg):
    print('Func i1', msg.topic, msg.payload)

i1 = Mqtt('/test',i1func)
# i1.unsubscribe()
#
# print(i1.__dict__)

while True:
    time.sleep(1)
    i1.publish('hallo', '/test2')


# Mqtt.onMessage(None, None, Msg('test','payload'))

# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message

# client.connect("iot.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.loop_forever()
