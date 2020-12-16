from z3 import *

def xorshift(x):
    x ^= x << 13
    x ^= LShR(x, 17)
    x ^= x << 5
    return x

def undo(x): # undo xorshift()
    assert x & 0xffffffff == x
    s = Solver()
    seed = BitVec('seed', 32)
    s.add(xorshift(seed) == x)
    assert str(s.check()) == 'sat'
    return s.model().eval(seed).as_long()

def initial_solve(r1,g1,b1, r2,g2,b2):
    r1,g1,b1,r2,g2,b2 = r1 & 0xff,g1 & 0xff,b1 & 0xff,r2 & 0xff,g2 & 0xff,b2&0xff

    c1 = r1 | (g1 << 8) | (b1 << 16)
    c2 = r2 | (g2 << 8) | (b2 << 16)
    print(hex(c1))
    print(hex(c2))
    s = Solver()
    seed = BitVec('seed', 32)
    
    s.add((seed & 0xffffff) == c1)

    # rotation 2
    seed = xorshift(seed)

    seed = xorshift(seed)
    s.add((seed & 0xffffff) == c2)

    assert str(s.check()) == 'sat'
    return s.model().eval(seed).as_long()

def full_solve(r1,g1,b1, r2,g2,b2, n):
    seed = initial_solve(r1,g1,b1, r2,g2,b2)
    # now we have the final seed value
    
    rotations = [None] * n
    for i in range(n-1, -1, -1):
        seed = undo(seed) # undo next() for color
        rotation = (seed % 36)*10
        seed = undo(seed) # undo next() for rotation
        rotations[i] = rotation

    positions = [None] * n
    for i in range(n-1, -1, -1): # now we can get the y's and x's
        y = float_val(seed)
        seed = undo(seed)
        x = float_val(seed)
        seed = undo(seed)
        positions[i] = (x,y)
        print(x,y,rotations[i])

    return positions,rotations

def float_val(int32_val):
    return int32_val / float(0xffffffff)

# print(hex(undo(0x9e299bad)))
# print(hex(full_solve(15,-56,94,-118,-87,99)))
# exit()

import win32api, win32con, win32gui
import time

tolerance = 0.1
def drag_piece(hwnd,src_x,src_y, dst_x,dst_y,scroll):
    src_x,src_y = win32gui.ClientToScreen(hwnd, (src_x, src_y))
    dst_x,dst_y = win32gui.ClientToScreen(hwnd, (dst_x, dst_y))
    dx,dy = dst_x - src_x, dst_y - src_y
    print(src_x,src_y)
    print(dst_x,dst_y)

    win32gui.SetForegroundWindow(hwnd)
    time.sleep(tolerance)
    win32api.SetCursorPos((src_x,src_y))
    time.sleep(tolerance)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
    time.sleep(tolerance)
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,int(scroll)*win32con.WHEEL_DELTA,0) # +scroll = forwards = clockwise
    time.sleep(tolerance)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP|win32con.MOUSEEVENTF_MOVE,dx,dy,0,0)
    time.sleep(tolerance)

def get_hdc():
    hwnd = win32gui.FindWindow(None, "Kokoro@kokoro")
    if not hwnd:
        print ('Window not found')
        exit(1)
    hdc = win32gui.GetDC(hwnd)
    assert hdc
    return hwnd,hdc

def get_top_color(hdc):
    color = win32gui.GetPixel(hdc, 369,490)
    r,g,b = color&0xff,(color>>8)&0xff,(color>>16)&0xff
    return r,g,b

def xy_to_client(x,y):
    return int(x*736),int(y*983) # image width and height

hwnd,hdc = get_hdc()

# record top piece color
r2,g2,b2=get_top_color(hdc)
print(hex(r2),hex(g2),hex(b2))

# reveal second to top piece. move the top piece off to the side
drag_piece(hwnd,369,490, 30, 490,0)
time.sleep(1.0) # for remote

# record second-to-top piece color
r1,g1,b1=get_top_color(hdc)
print(hex(r1),hex(g1),hex(b1))

n=50
positions,rotations = full_solve(r1,g1,b1,r2,g2,b2,n)

drag_piece(hwnd, 30, 490, *xy_to_client(*positions[n-1]), -rotations[n-1]/10.0)
for i in range(n-2, -1, -1):
    # time.sleep(0.5)
    drag_piece(hwnd, 369,490, *xy_to_client(*positions[i]), -rotations[i]/10.0)

exit()