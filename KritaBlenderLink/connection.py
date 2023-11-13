from krita import *
from threading import Timer,Thread
from multiprocessing import shared_memory
from multiprocessing.connection import Client

class ConnectionManager():
 adress = 6000
 connection = None
 shm = None
  
 def __init__(self,message_callback) -> None:
  self.message_callback = message_callback
  pass
 
 def change_adress(self,adr):
  self.adress = adr
 
 def connect(self,canvas_bytes_len,on_connect,on_disconnect):
  self.on_connect = on_connect
  self.on_disconnect = on_disconnect
  if(self.connection):
   return
  else: 
   print(self.connection)
  try:
    self.shm = shared_memory.SharedMemory(name="krita-blender", create=True, size=canvas_bytes_len)
  except:
    print("file exists, trying another way")
    self.shm = shared_memory.SharedMemory(name="krita-blender", create=False, size=canvas_bytes_len)
    
  def thread():
   with Client(("localhost",self.adress), authkey=b'2137') as connection:
    print("client created")
    self.connection = connection
    on_connect()
    while True:
     try:
      print("recived message")
      message = self.connection.recv()
      self.on_message(message)
     except:
      print("Error on reciving messages")
      self.connection = None
      if self.shm:
        self.shm.close()
        self.shm.unlink()
      on_disconnect()
      break
  t1 = Thread(target=thread)
  t1.start()
   
 def disconnect(self):
  if self.connection:
   self.connection.send('close')
   self.connection.close()
   self.connection = None
   if(self.on_disconnect):
     self.on_disconnect()
  if self.shm:
    self.shm.close()
    self.shm.unlink()
  else:
   print("there is no connection")
 def on_message(self,message):
  self.message_callback(message)
  print(message)
 
#  def on_disconnect():
#   print("disconnected from blender")

 def send_message(self,message):
  if self.connection:
    self.connection.send(message)
  else:
    print("there is no connection")
 def listen(message):
  pass

 def write_memory(self,bts):
  print(self.shm)
  if self.shm == None:
    print("no memory to write")
    return
  self.shm.buf[:len(bts)] = bts
   