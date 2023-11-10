from krita import *
from threading import Timer,Thread
from multiprocessing import shared_memory
from multiprocessing.connection import Client

class ConnectionManager():
 adress = 6000
 connection = None
 def __init__(self,message_callback) -> None:
  self.message_callback = message_callback
  pass
 
 def change_adress(self,adr):
  self.adress = adr
 
 def connect(self):
  if(self.connection):
   return
  else: 
   print(self.connection)
  def thread():
   with Client(("localhost",self.adress), authkey=b'2137') as connection:
    self.connection = connection
    while True:
     try:
      message = self.connection.recv()
      self.on_message(message)
     except:
      print("Error on reciving messages")
      self.connection = None
      break
  t1 = Thread(thread)
  t1.start()
   
 def disconnect(self):
  if self.connection:
   self.connection.send('close')
   self.connection.close()
   self.connection = None
  else:
   print("there is no connection")
 def on_message(self,message):
  self.message_callback(message)
  print(message)
 
 def on_disconnect():
  print("disconnected from blender")
 
 def send_message(self,message):
  self.connection.send(message)
  
 def listen(message):
  pass
   