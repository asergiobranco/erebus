from threading import Thread 
from multiprocessing import Manager, Queue 

class FakeClient(object):
    def __init__(self):
        pass 
    
    def sendall(message):
        pass

class ErebusHandler(Process):

    def __init__(self):
        super().__init__(self._handling)
        self.manager = Manager() 
        self.response_queue = Queue()
        self.clients = self.manager.list()
        self.workers = []
        self.responses = self.manager.dict()
    
    def send_process(self):
        while True:
            data_hash = self.response_queue.get()
            idx = self.response[data_hash]
            for i in range(len(self.clients)):
                try:
                    self.clients[idx - i].sendall([i, data_hash])
                except:
                    self.clean_client(idx-i)
    
    def _handling(self):
        p = Process(target=self.send_process)
        p.start()
        p.joi()
            

    def clean_client(self, idx):
        """Sets a fake client to avoid problems with the length while sending,
        and have to change all the idxs."""
        self.clients[idx] = FakeClient()

    def client_thread(self, client_socket, idx):
        while True:
            data = client_socket.recv(1024)
            if not data:
                self.clean_client(idx)
                break
            message = msgpack.unpackb(data)
            if message["data_hash"] not in self.responses:
                self.responses_lock.acquire()
                #double check
                if message["data_hash"] not in self.responses:
                    self.response[message["data_hash"]] = idx
                self.responses_lock.release()

    def add_worker(self, client_socket):
        self.locker.acquire()
        try:
            idx = len(self.clients)
            self.clients.append(client_socket)
            self.workers = Thread(target=self.client_thread, client_socket, idx)
            self.workers[-1].start()
        except:
            pass
        finally:
            self.locker.release()

