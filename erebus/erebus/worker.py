from multiprocessing import Queue, Value 
from threading import Lock 
from .handler import ErebusHandler
import msgpack 
class ErebusWorker(object):

    def __init__(self, erebus_lock, erebus_dict):
        self.queue = Queue()
        self.lock = Lock()
        self.free = Value("i", 1)
        self.erebus = erebus_dict
        self.erebus_lock = erebus_lock
    
    def add_to_erebus(self, request, client_socket):

        program_id = request["program_id"]
        
        if not isinstance(program_id, str):
            client_socket.close()
            return 

        self.erebus_lock.acquire()
        
        try:
            if program_id not in self.erebus:
                self.erebus[program_id] = ErebusHandler()
                self.erebus[program_id].start()
                print("Adding worker to program", program_id)
        except Exception as e:
            print(e)
        
        self.erebus_lock.release()

        self.erebus[program_id].add_worker(client_socket)
    
    def handle_client(self, client_socket):
        print("handling client", client_socket)
        message = b''
        i = True
        #tries to read the entire request
        while i and len(message) < 1024:
            data = client_socket.recv(1024)
            print(data)
            
            #if client closes connectio, there is nothing to do
            if not data:
                break

            message += data

            # tries to unpack the full request
            # if it can, breaks the while           
            try:
                request = msgpack.unpackb(message)
                print("request", request)
                i = False
                break
            except Exception as w:
                pass 
        
        try:
            self.add_to_erebus(request, client_socket)
        except Exception as e:
            print(e)
            client_socket.close()
            
                
            
        
    
    def add_client(self, client_socket):
        print("adding", client_socket)
        self.queue.put(client_socket)
    
    def start(self):
        while True:
            self.lock.acquire()
            try:
                print("waiting queue...")
                self.handle_client(self.queue.get())
            except Exception as e:
                print(e)
            self.lock.release()

