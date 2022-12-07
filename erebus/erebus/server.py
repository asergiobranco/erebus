import socket 
from multiprocessing import Process, Manager
from threading import Lock
import msgpack


from .worker import ErebusWorker

class ErebusServer(object):

    def __init__(self, hostname, port, no_workers=10):
        self.port = int(port)
        self.hostname = socket.gethostbyname(hostname)
        self.address = (self.hostname, self.port)
        self.manager = Manager()
        self.erebus_lock = Lock()

        self.erebus = self.manager.dict()

        self.workers = [
            ErebusWorker(self.erebus_lock, self.erebus) for _ in range(no_workers)
        ]
        self.processes =[
            Process(target=worker.start) for worker in self.workers
        ]

        

    

    def start(self):

        for process in self.processes:
            process.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            #print("awaitng clients")
            server.bind(self.address)
            server.listen(1000)
            while True:
                print("working...")
                for worker in self.workers:
                    client = server.accept()
                    #print("new client")
                    worker.add_client(client[0])
