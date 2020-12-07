from bitstring import BitStream, pack, Bits
from collections import OrderedDict

def _check_align(val):
    if val <= 0:
        raise ValueError("Invalid align value: %d" % val)

    ct = 0
    tmp = val
    while tmp:
        ct += tmp & 1
        tmp >>= 1

    if ct != 1:
        raise ValueError("Invalid align value: %d" % val)

class SeqMemory(BitStream):
    def __init__(self, *args, **kwargs):
        super(BitStream, self).__init__(*args, **kwargs)
        self.__reloc_sub = kwargs.pop("reloc_val", 0xdeadbeef)
        self.__reloc = OrderedDict()
        self.__base = None

    def relocate(self, mem_off, base_off):
        mem_off *= 8
        if self.length < mem_off + 32:
            raise ValueError("Out of bounds")

        self.__reloc[mem_off] = base_off
        if self.__base == None:
            val = self.__reloc_sub
        else:
            val = (base_off + self.__base) & 0xffffffff
        self.writeat(mem_off, 'uintle:32', val, over_reloc = False)

    def rebase(self, base):
        self.__base = base
        for mem_off, base_off in self.__reloc.items():
            self.writeat(mem_off, 'uintle:32', (base_off + base) & 0xffffffff,
                    over_reloc = False)

    def write(self, fmt, val, **kwargs):
        self.writelist(fmt, val, **kwargs)

    def writeat(self, pos, fmt, val, **kwargs):
        self.writelistat(pos, fmt, val, **kwargs)

    def writelist(self, fmt, *vals, **kwargs):
        bs = pack(fmt, *vals, **kwargs)
        need = self.pos + bs.length - self.length
        if need > 0:
            self.append(BitStream(need)) 
        self.overwrite(bs, self.pos, kwargs.pop("over_reloc", True))

    def writelistat(self, pos, fmt, *vals, **kwargs):
        oldpos = self.pos
        self.pos = pos
        self.writelist(fmt, *vals, **kwargs)
        self.pos = oldpos

    def writereloc(self, base_off):
        self.relocate(self.pos // 8, base_off)
        self.pos += 32

    def readobj(self, **kwargs):
        align = kwargs.pop('align', 64)
        _check_align(align)
        align -= 1
        start = self.pos

        _, _, clsid = self.readlist('uintle:32,uintle:32,uintle:32')
        if clsid not in _objs:
            raise ValueError('Unknown object type 0x%08x' % clsid)

        ret = _objs[clsid].load(self, **kwargs)

        self.writepad((start - self.pos) & align)
        return ret

    def writeobj(self, auto, *args, **kwargs):
        align = kwargs.pop('align', 64)
        _check_align(align)
        align -= 1
        start = self.pos

        if type(auto) == type:
            clstype = auto
            obj = auto(*args)
        else:
            if args:
                raise TypeError("Expected only one argument")
            clstype = type(auto)
            obj = auto
            
        self.writelist('uintle:32,uintle:32,uintle:32', clstype.clsheader, 
                0, clstype.clsid)
        obj.dump(self, **kwargs)

        self.writepad((start - self.pos) & align)

    def writepad(self, size):
        need = self.pos + size - self.length
        if need > 0:
            self.append(BitStream(need)) 
        self.pos += size
    
    def overwrite(self, bs, pos=None, over_reloc=True):
        bs = Bits(bs)
        super(SeqMemory, self).overwrite(bs, pos)
        if over_reloc:
            for off in list(self.__reloc.keys()):
                if self._check_reloc_intersect(pos, pos + bs.length, off):
                    del self.__reloc[off]

    def _check_reloc_intersect(self, lower, upper, reloc):
        if lower <= reloc:
            return upper > reloc
        else: 
            return reloc + 32 > lower

class JHeap(object):
    clsheader = 0x5
    clsid = 0x00000829
    
    @staticmethod
    def load(mem):
        index, flag, carr = mem.readlist('intle:32,uintle:32,uintle:32')
        return JHeap(index, carr, flag)
    
    def __init__(self, index, carr, flag=0):
        self.index = index
        self.carr = carr
        self.flag = flag

    def dump(self, mem):
        mem.writelist('intle:32,uintle:32', self.index, 0)
        if self.carr < 0:
            mem.writereloc(-self.carr)
        else:
            mem.write('uintle:32', self.carr)

    def __str__(self):
        return str('[%08x]' % self.carr)

    def __repr__(self):
        return 'JHeap[%d]: [%08x]' % (self.index, self.carr)


class arr(object):
    clsheader = 0x1
    
    @classmethod
    def load(cls, mem):
        size = mem.read('intle:32')
        if size < 0:
            raise ValueError("Not a valid array size")
        arr = [0] * size
        for i in range(size):
            arr[i] = mem.read(cls.ele_fmt)
        return cls(arr)

    def __init__(self, arr):
        self.arr = arr
        self.size = len(arr) # allow to tamper with it!

    def dump(self, mem):
        cls = type(self)

        mem.write('intle:32', self.size)
        if self.arr:
            mem.writelist(','.join([cls.ele_fmt] * len(self.arr)), *self.arr)

    def __str__(self):
        return str(self.arr)

    def __repr__(self):
        return '%s: %s' % (type(self).__name__, self.arr)


class B_arr(arr):
    clsid = 0x00057339
    ele_fmt = 'intle:8'

    def __init__(self, arr):
        if type(arr) is str:
            arr = list(map(ord, arr))
        super(B_arr, self).__init__(arr)

        self.content = ''.join(map(chr, self.arr))

    def __str__(self):
        return self.content

class C_arr(arr):
    clsid = 0x000573f6
    ele_fmt = 'intle:16'

    def __init__(self, arr):
        if type(arr) is str:
            arr = list(map(ord, arr))
        super(C_arr, self).__init__(arr)

        self.content = ''.join(map(chr, self.arr))

    def __str__(self):
        return self.content


class String(object):
    clsid = 0x00044e15
    clsheader = 0x5
    
    @classmethod
    def load(cls, mem):
        ptr = mem.read('intle:32') & 0xffffffff
        return cls(ptr)

    def __init__(self, ptr):
        self.ptr = ptr

    def dump(self, mem):
        mem.write('intle:32', self.ptr)

class AppClassLoader:
    clsid = 0x0004e5d3

def to_bytes(auto, *args, **kwargs):
    mem = SeqMemory(length=0)
    mem.writeobj(auto, *args, **kwargs)
    return mem.bytes

_objs = {}

def register_object(cls):
    _objs[cls.clsid] = cls

for x in [JHeap, C_arr, String, B_arr]:
    register_object(x)
