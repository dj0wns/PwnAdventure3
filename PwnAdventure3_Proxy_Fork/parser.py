HIDE_KNOWN = True;
#HIDE_KNOWN = False;

def parse(data, port, origin):
  #ignore server data
  if port == 3333:
    return;
  
  #if origin == "server":
  #  return

  op = data.hex()[:4];

  #noop
  if op == "0000":
    return;
  
  #location op
  elif op == "6d76":
    x = data.hex()[4:12]
    y = data.hex()[12:20]
    z = data.hex()[20:28]
    rotation = data.hex()[28:36]
    if not HIDE_KNOWN:
      print("Location OP: {} - {} - {} - {} - {}".format(op,x,y,z,rotation))
  #weapon firing op
  elif op == "2a69":
    weaponID = data.hex()[4:8]
    unknown = data.hex()[8:68]
    posx = data.hex()[68:76]
    posy = data.hex()[76:84]
    posz = data.hex()[84:92]
    rot = data.hex()[92:100] 
    blank = data.hex()[100:108] 
    if not HIDE_KNOWN:
      print("Shoot OP: {} - weaponID: {} - position: {} - {} - {} - rotation: {} - Unknown - {} - {}".format(op,weaponID,posx,posy,posz,rot,blank,unknown))
  #kill projectile op
  elif op == "7878":
    projID = data.hex()[4:32]
    #if not HIDE_KNOWN:
    print("Projectile dead OP: {} - projectileID: {}".format(op,projID))

  else :
    #print unparsed ops
    print("{}({}) {}".format(origin, port, data.hex()))
