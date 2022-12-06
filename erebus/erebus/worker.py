from multiprocessing import Queue, Value, Manager, Process
from threading import Lock 
from .handler import ErebusHandler
import msgpack 
import socket
import time 
import os 


class ErebusWorker(object):

    def __init__(self, erebus_lock, erebus_dict):
        self.queue = Queue()
        self.lock = Lock()
        self.free = Value("i", 1)
        self.erebus = erebus_dict
        self.erebus_lock = erebus_lock
        self.manager = Manager()
    
    def add_to_erebus(self, request, client_socket):

        program_id = request["program_id"]
        
        #print("Adding to program id", program_id)
        if not isinstance(program_id, str):
            client_socket.close()
            return 

        self.erebus_lock.acquire()
        
        try:
            if program_id not in self.erebus:
                #print("Added to program id", program_id)
                self.erebus[program_id] = self.manager.list()
                ErebusHandler(self.erebus[program_id], program_id).start()
                #print("Adding worker to program", program_id)
        except Exception as e:
            print("here 4", e)
        i = 0
        while i < 5:
            try:
                time.sleep(0.2)
                self.add_client_to_erebus(client_socket, program_id)
                #print("client created")
                i=5
            except Exception as e:
                print("here 47", e)
                i+=1

            
        self.erebus_lock.release()

        #self.erebus[program_id].add_worker(client_socket)
    
    def add_client_to_erebus(self, client_socket, program_id):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            if not os.path.exists("/tmp/"+program_id+".s"):
                raise Exception("SOCKET DONT EXISTS")
            #print("connectig to: ", "/tmp/"+program_id+".s")
            s.connect("/tmp/"+program_id+".s")
            s.recv(1024)
            self.erebus[program_id].append(client_socket)
            time.sleep(0.01)
            #print("APPENDED TO CLIENTS")
            s.sendall(b'ok')
            s.recv(1024)

    
    def handle_client(self, client_socket):
        #print("handling client", client_socket)
        message = b''
        i = True
        #tries to read the entire request
        while i and len(message) < 1024:
            data = client_socket.recv(1024)
            #print(data)
            
            #if client closes connectio, there is nothing to do
            if not data:
                break

            message += data

            # tries to unpack the full request
            # if it can, breaks the while           
            try:
                request = msgpack.unpackb(message)
                #print("request", request)
                i = False
                break
            except Exception as w:
                print("handler 25", w)
        
        try:
            self.add_to_erebus(request, client_socket)
        except Exception as e:
            print("handle_client", e)
            client_socket.close()
            
                
            
        
    
    def add_client(self, client_socket):
        self.queue.put(client_socket)
    
    def start(self):
        while True:
            self.lock.acquire()
            try:
                #print("waiting queue...")
                self.handle_client(self.queue.get())
            except Exception as e:
                print("here 5",  e)
            self.lock.release()

