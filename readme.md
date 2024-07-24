This is a multithreaded implementation of a client-server chat with a chatbot

Server:
    The server listens to any incoming connections and new data in sockets using select.select()
    It accepts new connections, adding them to the client list.
    When the server gets a new message, it parses it and broadcasts it to everyone immediately.

Client:
    has different threads for sending and receiving messages.
    sending "quit" will close the socket and end the session.
    
AI:
    Will either write something relevant to the conversation, or randomly blur out insanities
    This behaviour can be changed ofcourse by changing the prompt


To build this, I had to learn a bit about sockets and Threading library, this took me an extra few hours to go through 
some how-to's.

Building the project end to end took about 1.5 days of work. But I'm pretty pleased with the result.  
There is a lot that can be added like tests, usernames, a db with tables for users and conversations, and more.