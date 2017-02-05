import paho.mqtt.client as mqtt
import time

def log(*msg):
    pass
    # print(msg)

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

    def __init__(self, server='localhost', username=None, password=None, port=1883):
        super(Mqtt, self).__init__()
        print('INIT!!!')
        self.__client = mqtt.Client()
        self.__mqttServer = server
        self.__mqttUsername = username
        self.__mqttPassword = password
        self.__mqttPort = port
        self.subscriptions = []
        self.openSubscriptions = []
        self.client = None
        self.userdata = None
        self.rc = None
        self.connected = False
    def _subscribe(self, sub):
        if not self.connected:
            self.openSubscriptions.append(sub)
            self.__connect()
            return sub
        self.subscriptions.append(sub)
        self.__client.subscribe(sub.topic)
        return sub
    def subscribe(self,topic,cb):
        log('Subscribe', topic)
        sub = Subscription(topic,cb)
        return self._subscribe(sub)
    def unsubscribe(self, sub):
        log('Unsubscribe', sub.topic)
        for ssub in self.subscriptions:
            log(sub,ssub)
            if sub == ssub:
                self.subscriptions.remove(sub)
                self.__client.unsubscribe(sub.topic)
    def publish(self, topic, payload):
        log('Publish topic', topic)
        if topic == None:
            topic = self.topic
        self.__client.publish(topic, payload, retain=True)
    def __connect(self):
        log('Connect', self.__mqttServer)
        if self.__mqttUsername and self.__mqttPassword:
            self.__client.username_pw_set(self.__mqttUsername, self.__mqttPassword)
        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message
        self.__client.on_subscribe = self.on_subscribe
        self.__client.connect_async(self.__mqttServer, self.__mqttPort, 60)
        self.__client.loop_start()
    def __disconnect(self):
        self.__client.disconnect()
    def on_message(self, client, userdata, msg):
        log('Message reseived at topic', msg.topic)
        calls = []
        for sub in self.subscriptions:
            result = mqtt.topic_matches_sub(sub.topic, msg.topic)
            if result:
                calls.append(sub)
        for call in calls:
            call.cb(msg)
    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass
    def on_connect(self, client, userdata, flags, rc):
        self.connected = True
        log('Connected', self.__mqttServer)
        if len(self.openSubscriptions) > 0:
            for sub in self.openSubscriptions:
                log('Subscribe:',sub.topic)
                self._subscribe(sub)
            self.openSubscriptions = []
        self.client = client
        self.userdata = userdata
        self.rc = rc
    def on_disconnect(self, client, userdata, rc):
        log('Disconnected')
        self.client = None
        self.userdata = None
        self.rc = None
        self.connected = False
