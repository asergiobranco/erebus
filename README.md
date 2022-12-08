# erebus

```mermaid
flowchart TB;
    MainServer-- Turn Light On -->Worker1;
    MainServer-- Turn Light On -->Worker2;
    MainServer-- Turn Light On -->Worker3;
    Worker1-- Turn Light On --> Client;
    Worker2-- Turn Light On --> Client;
    Worker3-- Turn Light On --> Client;
    Client-.-What["What to do?"]
```

```mermaid
flowchart TB;
    MainServer-- Turn Light On -->Worker1;
    MainServer-- Turn Light On -->Worker2;
    MainServer-- Turn Light On -->Worker3;
    Worker1-- Can Execute? --> Erebus;
    Worker2-- Can Execute? --> Erebus;
    Worker3-- Can Execute? --> Erebus;
    Erebus-.-Y["Responds YES only to Worker3"]
    Worker3-- Turn Light On --> Client;
    Client-.-T["Turn Light On"]
```

```mermaid
sequenceDiagram
    participant Worker
    participant Erebus
    Worker->>+Erebus: {"program_id" : $PROGRAM_ID}
    Erebus->>-Worker: { "c" : $CODE, "m" : $MESSAGE}
    loop Every 60 seconds
        Erebus->>Worker : [$i, "keep_alive"]
    end
    Worker->>+Erebus: {"data_hash" : $DATA_HASH}
    Erebus->>-Worker: [$i, $DATA_HASH]
    Note right of Erebus: Every communication is msgpack Serialized
 ```
    
## Client Example

```python
import socket 
import msgpack

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("erebusip", 8000))
    s.sendall(
        msgpack.packb({"program_id" : MYUNIQUEID})
    )
    # wait for server to tell you it could add you
    s.recv(1024)

    # Do something waiting for a request from another service

    s.sendall(
        msgpack.packb({"data_hash" : UNIQUE_ID_FOR_DATA_REQUEST})
    )

    response = msgpack.unpackb(s.recv(1024))

    if response[0] == 0:
        # RUN THE CODE
    else:
        # OTHER WORKER WAS FASTER THAN YOU

```
