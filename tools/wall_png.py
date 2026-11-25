#!/usr/bin/env python3
"""Draws the Wall of Deeds (art/monde/mur.png via `tools/wall_png.py | convert pam:- PNG32:art/monde/mur.png`): an isometric crenellated stone wall, one logical px per pixel.

Its front face runs down-right at the 2:1 iso slope and faces the viewer (south-west), so a hero standing
in front of it, back turned, has a hand on the stones. Geometry is shared with lieux.js (WALL).
"""
import sys

L, H, DEPTH = 150, 36, 12  # face length (x), wall height, wall thickness (x; y is half)
MERLON, Y0 = 6, 50  # merlon height; y of the face's bottom-left corner
W, HT = L + DEPTH + 2, Y0 + L // 2 + 3

STONE = ["#9a96a0", "#8b8792", "#a7a3ad", "#837f8b"]
MORTAR, SIDE, SIDE_M, TOP, TOP_D = "#5d5966", "#6c6875", "#4d4957", "#b8b4bd", "#a19da8"
OUTLINE, MOSS, MOSS_L = "#1b1420", "#4f7a32", "#6d9b43"
WALK, WALK_L = "#6f6b78", "#5d5966"

px = {}


def put(x, y, c):
    if 0 <= x < W and 0 <= y < HT:
        px[(x, y)] = c


def h(*v):
    n = 2166136261
    for a in v:
        n = ((n ^ (a & 0xFFFF)) * 16777619) & 0xFFFFFFFF
    return n


def merlon(x):
    return (x // 7) % 2 == 0


# walkway on top, painted back to front; merlons only on the front parapet (PARAPET px deep)
PARAPET = 4
for k in range(DEPTH - 1, -1, -1):
    for x in range(k, L + k):
        yl = Y0 + x // 2 - H - k
        if k < PARAPET and merlon(x - k):
            put(x, yl - MERLON, TOP)
            for y in range(yl - MERLON + 1, yl + 1):
                put(x, y, SIDE if k else TOP_D)
        else:
            put(x, yl, WALK_L if (x - k) % 10 == 0 else WALK)

# front face (lit), raised by a merlon every other 7 px
for x in range(L):
    yb = Y0 + x // 2
    top = yb - H - (MERLON if merlon(x) else 0)
    for y in range(top, yb + 1):
        v = yb - y  # height above the ground
        course = v // 6
        jog = 8 if course % 2 else 0
        if v % 6 == 0 or (x + jog) % 16 == 0:
            c = MORTAR
        else:
            c = STONE[h((x + jog) // 16, course) % len(STONE)]
            if v <= 4 and h(x, y, 7) % 5 < 2:
                c = MOSS if h(x, y) % 3 else MOSS_L
        put(x, y, c)

# the end face (shade)
for k in range(DEPTH + 1):
    x = L - 1 + k
    yb = Y0 + (L - 1) // 2 - k // 2
    for y in range(yb - H - (MERLON if merlon(L - 1) else 0), yb + 1):
        put(x, y, SIDE_M if (yb - y) % 6 == 0 else SIDE)

# 1 px dark outline round the whole shape
shape = set(px)
for (x, y) in list(shape):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if (x + dx, y + dy) not in shape:
            put(x + dx, y + dy, OUTLINE)

def rgb(c):
    return bytes(int(c[i:i + 2], 16) for i in (1, 3, 5))


body = b"".join(rgb(px[(x, y)]) + b"\xff" if (x, y) in px else b"\0\0\0\0" for y in range(HT) for x in range(W))
sys.stdout.buffer.write(f"P7\nWIDTH {W}\nHEIGHT {HT}\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n".encode() + body)
print(f"{W}x{HT}", file=sys.stderr)
