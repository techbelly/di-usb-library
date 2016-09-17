import threading
from collections import defaultdict
import hidapi

class InfinityComms(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.device = self.initBase()
	self.finish = False
        self.pending_requests = {}
        self.message_number = 0
        self.observers = []

    def initBase(self):
        hidapi.hid_init()
        device = hidapi.hid_open(0x0e6f, 0x0129)
	hidapi.hid_set_nonblocking(device, False)
        return device

    def run(self):
        while not self.finish:
            line = hidapi.hid_read_timeout(self.device,32,3000)

            if not len(line):
                continue

            fields = [c for c in line]
            if fields[0] == 0xaa:
                length = fields[1]
                message_id = fields[2]
                if message_id in self.pending_requests:
                    deferred = self.pending_requests[message_id]
                    deferred.resolve(fields[3:length+2])
                    del self.pending_requests[message_id]
                else:
                    self.unknown_message(line)
            elif fields[0] == 0xab:
                self.notifyObservers()
            else:
                self.unknown_message(line)

    def addObserver(self, object):
        self.observers.append(object)

    def notifyObservers(self):
        for obs in self.observers:
            obs.tagsUpdated()

    def unknown_message(self, fields):
        print("UNKNOWN MESSAGE RECEIVED ", fields)

    def next_message_number(self):
        self.message_number = (self.message_number + 1) % 256
        return self.message_number

    def send_message(self, command, data = []):
        message_id, message = self.construct_message(command, data)
        result = Deferred()
        self.pending_requests[message_id] = result
        hidapi.hid_write(self.device, message)
        return Promise(result)

    def construct_message(self, command, data):
        message_id = self.next_message_number()
        command_body = [command, message_id] + data
        command_length = len(command_body)
        command_bytes = [0x00, 0xff, command_length] + command_body
        message = [0x00] * 33
        checksum = 0
        for (index, byte) in enumerate(command_bytes):
            message[index] = byte
            checksum = checksum + byte
        message[len(command_bytes)] = checksum & 0xff
        return (message_id, map(chr, message))


class Deferred(object):
    def __init__(self):
	self.event = threading.Event()
        self.rejected = False
        self.result = None

    def resolve(self, value):
        self.rejected = False
        self.result = value
        self.event.set()

    def wait(self):
        while not self.event.is_set():
            self.event.wait(3)


class Promise(object):
    def __init__(self, deferred):
        self.deferred = deferred

    def then(self, success, failure=None):
        def task():
            try:
                self.deferred.wait()
                result = self.deferred.result
                success(result)
            except Exception as ex:
                if failure:
                    failure(ex)
                else:
                    print(ex.message)
        threading.Thread(target=task).start()
        return self

    def wait(self):
        self.deferred.wait()


class InfinityBase(object):
    def __init__(self):
        self.comms = InfinityComms()
        self.comms.addObserver(self)
        self.onTagsChanged = None

    def connect(self):
        self.comms.daemon = True
        self.comms.start()
        self.activate()

    def disconnect(self):
        self.comms.finish = True

    def activate(self):
        activate_message = [0x28,0x63,0x29,0x20,0x44,
                            0x69,0x73,0x6e,0x65,0x79,
                            0x20,0x32,0x30,0x31,0x33]
        self.comms.send_message(0x80, activate_message)

    def tagsUpdated(self):
        if self.onTagsChanged:
            self.onTagsChanged()

    def getAllTags(self, then):
        def queryAllTags(idx):
            if len(idx) == 0:
                then(dict())
            numberToGet = [0] * len(idx)
            tagByPlatform = defaultdict(list)
            for (platform, tagIdx) in idx:
                def fileTag(platform):
                    def inner(tag):
                        tagByPlatform[platform].append(tag)
                        numberToGet.pop()
                        if len(numberToGet) == 0:
                            then(dict(tagByPlatform))
                    return inner
                self.getTag(tagIdx, fileTag(platform))
        self.getTagIdx(queryAllTags)

    def getTagIdx(self, then):
        def parseIndex(bytes):
            values = [ ((byte & 0xF0) >> 4, byte & 0x0F ) for byte in bytes if byte != 0x09]
            then(values)
        self.comms.send_message(0xa1).then(parseIndex)

    def getTag(self, idx, then):
        self.comms.send_message(0xb4, [idx]).then(then)

    def setColor(self, platform, r, g, b):
        self.comms.send_message(0x90, [platform, r, g, b])

    def fadeColor(self, platform, r, g, b):
        self.comms.send_message(0x92, [platform, 0x10, 0x02, r, g, b])

    def flashColor(self, platform, r, g, b):
        self.comms.send_message(0x93, [platform, 0x02, 0x02, 0x06, r, g, b])

if __name__ == '__main__':
    import time

    def futurePrint(s):
        print(s)

    base = InfinityBase()

    base.onTagsChanged = lambda: futurePrint("Tags added or removed.")

    base.connect()

    base.getAllTags(futurePrint)

    base.setColor(1, 200, 0, 0)

    base.setColor(2, 0, 56, 0)

    base.fadeColor(3, 0, 0, 200)

    time.sleep(3)

    base.flashColor(3, 0, 0, 200)

    print("Try adding and removing figures and discs to/from the base. CTRL-C to quit")
    while True:
        pass

