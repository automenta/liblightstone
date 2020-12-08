import ctypes, pygame, sys
from pygame.locals import *
from ctypes import *

# Contains lightstone device readings
class lightstone_info(Structure):
    _fields_ = [("hrv", c_float), ("scl", c_float)]

class lightstone():
    def __init__(self):

        # Open DLL
        self.dll = ctypes.CDLL("d:\\lightstone\py\lightstone.dll")

        # Define argument types & return types for all methods
        self._create = self.dll.lightstone_create
        self._create.argtypes = []
        self._create.restype = c_void_p

        self._delete = self.dll.lightstone_delete
        self._delete.argtypes = [c_void_p]        
        
        self._count = self.dll.lightstone_get_count
        self._count.restype = c_int
        self._count.argtypes = [c_void_p]

        self._open = self.dll.lightstone_open
        self._open.restype = c_int
        self._open.argtypes = [c_void_p, c_uint]

        self._get_info = self.dll.lightstone_get_info
        self._get_info.restype = lightstone_info
        self._get_info.argtypes = [c_void_p]

        self._valid = self.dll.lightstone_valid
        self._valid.restype = c_int
        self._valid.argtypes = [c_void_p]

        self._close = self.dll.lightstone_close
        self._close.restype = c_int
        self._close.argtypes = [c_void_p]

        # Call lightstone_create
        self.ptr = self._create()

    # Destructor, calls lightstone_delete
    def __del__(self):
        self._delete(self.ptr)        

    # Return count of lightstone devices
    def count(self):
        return self._count(self.ptr)

    # Open given lightstone device
    def open(self, idx):
        return self._open(self.ptr, idx)

    # Return device readings
    def get_info(self):
        return self._get_info(self.ptr)

    # Returns > 0 if device is initalized, 0 otherwise
    def valid(self):
        return self._valid(self.ptr)

    # Close opened lightstone device
    def close(self):
        return self._close(self.ptr)

WID=1500
HGT=480
pygame.init()
fpsClock = pygame.time.Clock()
windowSurfaceObj = pygame.display.set_mode((WID,HGT))
pygame.display.set_caption('Lightstone')
red = pygame.Color(255,0,0)
blue = pygame.Color(0,0,255)
white = pygame.Color(255,255,255)
grey = pygame.Color(200,200,200)
    
stone = lightstone()
print "Counted lightstones: "+str(stone.count())
print "Opening lightstone: "
res = stone.open(0)
if res == 0:
    print "Success!"
else:
    print "Failure: "+str(res)

val = val2 = stone.get_info()
x2 = 0
x = 1

windowSurfaceObj.fill(white)

font = pygame.font.Font('freesansbold.ttf', 16)

hearts = list()
rate=0
avgbeat = 0

for i in range(200):
    hearts.append((i/1000, i))

print [xx[0] for xx in hearts[i-3:i+3]]
#sys.exit(0)
x=0
irate=irate2=0
rate2=0
FWD=14
REV=14
while True:
                
    val = stone.get_info()
    while val.hrv == 0.0:
        val = stone.get_info()

    hearts.append((val.hrv, pygame.time.get_ticks()))
    s = 0
    for i in hearts:
        s = s + i[0]
    avg = s / len(hearts)
    #avg = sum(hearts) / len(hearts)
    t0 = 0
    beats = list()
    for i in range(REV, len(hearts)-FWD):
        v = hearts[i][0]
        t = hearts[i][1]
        if v > avg and v >= max([xx[0] for xx in hearts[i-REV:i+FWD]]):
            if t0 > 0:
                beats.append(t-t0)
            t0 = t
                
    if len(beats) > 0 and sum(beats) > 0:
        weights = list()
        for i in range(len(beats)):
            weights.append(i)
        top = sum(beats[ii] * weights[ii] for ii in range(len(beats)))
        bot = sum(weights[ii] for ii in range(len(beats)))
        print str(top)+" / "+str(bot)
        avgbeat = float(top) / float(bot) if bot != 0 else 0
        rate = 60000.0 / float(avgbeat) if avgbeat != 0 else 0
                
    hearts.pop(0)

    pygame.draw.rect(windowSurfaceObj, white, (20, 10, WID, 50))
            
    msg = font.render(str(round(rate)), False, red)
    msgRect = msg.get_rect()
    msgRect.topleft = (20, 10)
    windowSurfaceObj.blit(msg, msgRect)

    msg = font.render(str(round(irate)), False, grey)
    msgRect = msg.get_rect()
    msgRect.topleft = (80, 10)
    windowSurfaceObj.blit(msg, msgRect)


    i = len(hearts) - 15

    irate = 60000.0 / float(beats[len(beats)-1]) if len(beats)>0 else 0
        
    pygame.draw.line(windowSurfaceObj, blue, (x-1, 480-hearts[i-1][0]*100), (x, 480-hearts[i][0]*100))

    pygame.draw.line(windowSurfaceObj, grey, (x2-1, 200-irate2), (x2, 200-irate))
    pygame.draw.line(windowSurfaceObj, red, (x2-1, 200-rate2), (x2, 200-rate))
    rate2 = rate
    irate2= irate

    v = hearts[i][0]
    if v > avg and v >= max([xx[0] for xx in hearts[i-REV:i+FWD]]):
        pygame.draw.rect(windowSurfaceObj, red, (x-2, 480-(hearts[i][0]*100)-2, 4, 4)) 

    print str(v)+" / "+str(avg)+" M: "+str(max([xx[0] for xx in hearts[i-REV:i+FWD]]))+" B: "+str(beats[len(beats)-1] if len(beats)>0 else 0)

    val2 = val
    
    x = x+1
    if(x>=WID):
        pygame.draw.rect(windowSurfaceObj, white, (0, 170,WID,HGT))
        x = 1

    x2 = x2 + 0.25
    if(x2>=WID):
        pygame.draw.rect(windowSurfaceObj, white, (0, 0, WID,170))
        x2 = 1

    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(30)
        
