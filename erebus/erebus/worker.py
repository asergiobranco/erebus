from multiprocessing import Queue, Value 
from threading import Lock 
from .handler import ErebusHandler

class ErebusWorker(object):

    def __init__(self, erebus_lock, erebus_dict):
        self.queue = Queue()
        self.lock = Lock()
        self.free = Value("i", 1)
        self.erebus = erebus_dict
        self.erebus_lock = erebus_lock
    
    def add_to_erebus(self, request, client_socket):
        self.erebus_lock.acquire()
        
        try:
            if request["program_id"] not in self.erebus:
                self.erebus[request["program_id"]] = ErebusHandler()
                self.erebus[request["program_id"]].start()
        except Exception as e:
            print(e)
        
        self.erebus_lock.release()

        self.erebus[request["program_id"]].add_worker(client_socket)
    
    def handle_client(self, client_socket):
        request = b''
        while len(request) < 2048:
            data = client.recv(1024)
            if not data:
                break
            request += data
        
        try:
            request = msgpack.unpackb(request)
        except:
            client.close()
            return 
    
    def add_client(self, client_socket):
        self.queue.put(client_socket)
    
    def start(self):
        while True:
            self.lock.acquire()
            try:
                self.handle_client(self.queue.get())
            except Exception as e:
                pass
            self.lock.release()

