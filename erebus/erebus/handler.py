from threading import Thread, Lock, Timer
from multiprocessing import Manager, Queue, Process, Value
import msgpack 
from secrets import token_urlsafe
import socket
import time 


class FakeClient(object):
    def __init__(self):
        pass 
    
    def sendall(self, message):
        pass

class ErebusHandler(Process):

    def __init__(self, client_list, program_id):
        super().__init__(target=self._handling)
        self.manager = Manager() 
        self.response_queue = Queue()
        #self.clients = self.manager.list()
        self.workers = []
        self.responses = self.manager.dict()
        self.responses["keep_alive"] = 0
        self.no_clients = Value("i", 0)
        self.locker = Lock()
        self.responses_lock = Lock()
        self.l = token_urlsafe()
        self.clients = client_list
        self.program_id = program_id
        self._response_cliente_created = msgpack.packb({"c" : 200, "m" : "ok"})
    
    def keep_alive(self):
        #print("running timer...", len(self.clients ))
        self.response_queue.put("keep_alive")
        self.start_keep_alive_timer()
    
    def start_keep_alive_timer(self):
        self.keep_alive_timer = Timer(60.0, self.keep_alive)
        self.keep_alive_timer.start()
    
    def reset_keep_alive_timer(self):
        try:
            self.keep_alive_timer.cancel()
        except Exception as e:
            print("here 1",e)
        finally:
            self.start_keep_alive_timer()

    def send_process(self):
        #print("starting timer")
        self.start_keep_alive_timer()
        while True:
            try:
                data_hash = self.response_queue.get()
                self.reset_keep_alive_timer()
                idx = self.responses[data_hash]
                for i in range(len(self.clients)):
                    try:
                        #print([idx, i, data_hash], len(self.clients))
                        self.clients[idx - i].sendall(
                            msgpack.packb([i, data_hash])
                        )
                    except Exception as e:
                        print("here 2",e)
                        self.clean_client(idx-i)
            except Exception as e:
                print(e)
    
    def init_server(self):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind("/tmp/"+self.program_id + ".s")
            #print("created: ", "/tmp/"+self.program_id + ".s")
            while True:
                s.listen(1)
                #print("awaiting client inn socket", "/tmp/"+self.program_id + ".s")
                client, addr = s.accept()
                client.sendall(b'ok')
                client.recv(1024)
                self.add_worker()
                client.shutdown(socket.SHUT_RDWR)
                client.close()
        

    def _handling(self):
        #print("starting process")
        
        p = Process(target=self.send_process)
        p.start()
        self.init_server()

    def clean_client(self, idx):
        """Sets a fake client to avoid problems with the length while sending,
        and have to change all the idxs."""
        self.clients[idx] = FakeClient()

    def client_thread(self, client_socket, idx):
        #print("starting", idx)
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
                    self.responses[message["data_hash"]] = idx
                    self.response_queue.put(message["data_hash"])
                self.responses_lock.release()

    def add_worker(self):
        self.locker.acquire()
        try:
            
            idx = self.no_clients.value
            #print(len(self.clients), self.no_clients.value)
            while (len(self.clients) == self.no_clients.value):
                print("waiting for append...", len(self.clients), self.no_clients.value)
                time.sleep(0.1)
            self.no_clients.value += 1
            #print("appended", idx, self.clients)
            #self.clients.append(client_socket)
            #print(self.clients)
            self.workers.append(Thread(target=self.client_thread, args = (self.clients[-1], idx)))
            #print(self.l,self.workers)
            self.workers[-1].start()
            self.clients[-1].sendall(self._response_cliente_created)

        except Exception as e:
            print("here 3", e)
        finally:
            self.locker.release()

