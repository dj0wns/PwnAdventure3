import socket
import os
import importlib
import queue
from threading import Thread

import parser
import packet

class ProxyToServer(Thread):

  def __init__(self, host, port):
    super(ProxyToServer, self).__init__()
    self.game = None #game client socket not known yet
    self.port = port
    self.host = host
    self.sendQueue = queue.Queue()
    #Socket example taken from python docs
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.connect((host, port))

  #run in thread
  def run(self):
    while True:
      data = self.server.recv(4096)
      if data:
        #Realtime updating of parser without restarting proxy
        try:
          importlib.reload(parser)
          parser.parse(data, self.port, 'server')
        except Exception as e:
          print('server[{}]'.format(self.port),e)
        # forward to client
        self.game.sendall(data)
      if not self.sendQueue.empty():
        item = self.sendQueue.get()
        self.server.sendall(item)

class GameToProxy(Thread):
  def __init__(self, host, port):
    super(GameToProxy, self).__init__()
    self.server = None # real server socket not known yet
    self.port = port
    self.host = host
    self.sendQueue = queue.Queue()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host,port))
    sock.listen(1)
    self.game, addr = sock.accept()

  def run(self):
    while True:
      data = self.game.recv(4096)
      if data:
        #Realtime updating of parser without restarting proxy
        try:
          importlib.reload(parser)
          parser.parse(data, self.port, 'client')
        except Exception as e:
          print('client[{}]'.format(self.port),e)
        #forward to server
        self.server.sendall(data)

#Master controller of a socket proxy
class Proxy(Thread):
  def __init__(self, from_host, to_host, from_port, to_port):
    super(Proxy, self).__init__()
    self.from_host = from_host
    self.to_host = to_host
    self.from_port = from_port
    self.to_port = to_port

  def run(self):
    while True:
      print("[proxy(from {} - to {}) ] setting up".format(self.from_port, self.to_port))
      self.g2p = GameToProxy(self.from_host, self.from_port)
      print("Listening on {}".format(self.from_port))
      self.p2s = ProxyToServer(self.to_host, self.to_port)
      print("Sending to {}".format(self.to_port))
      print("[proxy(from {} - to {})] connection established".format(self.from_port, self.to_port))
      #give each thread the reference to the other
      self.g2p.server = self.p2s.server
      self.p2s.game = self.g2p.game

      self.g2p.start()
      self.p2s.start()

if __name__ == "__main__":
  master_server = Proxy('0.0.0.0', '192.168.1.10', 3333, 3333)
  master_server.start()
  

  #name and keep references to game servers
  game_server0 = Proxy('0.0.0.0','192.168.1.10',3000,3000)
  game_server1 = Proxy('0.0.0.0','192.168.1.10',3001,3001)
  game_server2 = Proxy('0.0.0.0','192.168.1.10',3002,3002)
  game_server3 = Proxy('0.0.0.0','192.168.1.10',3003,3003)
  game_server4 = Proxy('0.0.0.0','192.168.1.10',3004,3004)
  game_server5 = Proxy('0.0.0.0','192.168.1.10',3005,3005)
  game_server0.start()
  game_server1.start()
  game_server2.start()
  game_server3.start()
  game_server4.start()
  game_server5.start()

  #execute commands while monitoring is running
  while True:
    try:
      cmd = input('$ ')
      importlib.reload(packet)
      if cmd[:4] == 'quit':
        os._exit(0)
      elif cmd[:4] == 'fire':
        game_server0.p2s.sendQueue.put(packet.GRENADE_PACKET)
    except Exception as e:
      print(e)
