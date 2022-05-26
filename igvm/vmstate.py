from ctypes import *
from enum import Enum

from igvm.bootcstruct import *


PGSHIFT = 12
PGSIZE = (1 << PGSHIFT)
_PAGE_ENCRYPTED = (1 << 51)
_PAGE_PRESENT = (1 << 0)
_PAGE_RW = (1 << 1)
_PAGE_USER = (1<< 2)
_PAGE_PAGE_PSE = (1<< 7)
_PAGE_RW_U_P = (_PAGE_PRESENT | _PAGE_RW | _PAGE_USER )

PAT_UC = 0
PAT_WC = 1
PAT_WT = 4
PAT_WP = 5
PAT_WB = 6
PAT_UC_MINUS = 7

def pat(index: int, val: int):
    return val << (8*index)

PAT_RESET_VAL = pat(0, PAT_WB) | pat(1, PAT_WT) | pat(2, PAT_UC_MINUS) |  pat(3, PAT_UC) | pat(4, PAT_WB) | pat(5, PAT_WT) | pat(6, PAT_UC_MINUS) |  pat(7, PAT_UC)
assert(PAT_RESET_VAL == 0x0007040600070406)

class ARCH(Enum):
    X86 = 'x86'
    X64 = 'x64'


class SegAttr(Structure):
    _fields_ = [('type', c_uint16, 4),
                ('s', c_uint16, 1),
                ('dpl', c_uint16, 2),
                ('p', c_uint16, 1),
                ('avl', c_uint16, 1),
                ('l', c_uint16, 1),
                ('db', c_uint16, 1),
                ('g', c_uint16, 1),
                ('rsvd0', c_uint16, 4)]

class UnionSegAttr(Union):
     _fields_ = [("reg", SegAttr), ("val", c_uint16)]

class GdtEntry(struct_desc_struct):
    def __init__(self, base = 0, limit = 0, type = 0, s = 0, dpl = 0, p = 0, l = 0, db = 0, g = 0):
        self.limit0=limit
        self.limit1=(limit>>16)&0xF
        self.base0=base
        self.base1=(base>>16)&0xFF
        self.base2=(base>>24)&0xFF
        self.type= type

        self.s=s
        self.dpl=dpl
        self.p=p

        self.avl = 0
        self.l=l
        self.d=db
        self.g=g

    @property
    def base(self) -> c_uint32:
        return self.base0 | (self.base1 << 16) | (self.base2 << 24)

    @property
    def limit(self) -> c_uint32:
        return self.limit0 | (self.limit1 << 16)

    @property
    def attribute(self) -> c_uint16:
        attr = UnionSegAttr()
        attr.reg.type = self.type
        attr.reg.s = self.s
        attr.reg.dpl= self.dpl
        attr.reg.p = self.p
        attr.reg.avl = self.avl
        attr.reg.l = self.l
        attr.reg.db = self.d
        attr.reg.g  = self.g
        return attr.val

class p4d_t(Structure):
    _pack_ = 1
    _fields_ = [('val', c_uint64)]

class pgd_t(Structure):
    _pack_ = 1
    _fields_ = [('val', c_uint64)]

class RegCr4(Structure):
    _pack_ = 1
    _fields_ = [('VME', c_uint32, 1),
                ('PVI', c_uint32, 1),
                ('TSD', c_uint32, 1),
                ('DE', c_uint32, 1),
                ('PSE', c_uint32, 1),
                ('PAE', c_uint32, 1),
                ('MCE', c_uint32, 1),
                ('PGE', c_uint32, 1),
                ('PCE', c_uint32, 1),
                ('OSFXSR', c_uint32, 1),
                ('OSXMMEXCPT', c_uint32, 1),
                ('UMIP', c_uint32, 1),
                ('rsvd0', c_uint32, 1),
                ('VMXE', c_uint32, 1),
                ('SMXE', c_uint32, 1),
                ('rsvd1', c_uint32, 1),
                ('FSGSBASE', c_uint32, 1),
                ('PCIDE', c_uint32, 1),
                ('OSXSAVE', c_uint32, 1),
                ('rsvd2', c_uint32, 1),
                ('SMEP', c_uint32, 1),
                ('SMAP', c_uint32, 1),
                ('PKE', c_uint32, 1),
                ('rsvd3', c_uint32, 9)]

assert sizeof(RegCr4) == 4

class UnionRegCr4(Union):
    _fields_ = [("reg", RegCr4), ("val", c_uint32)]

class RegEflags(Structure):
    _pack_ = 1
    _fields_ = [('CF', c_uint32, 1),
                ('one', c_uint32, 1),
                ('PF', c_uint32, 1),
                ('rsvd0', c_uint32, 1),
                ('AF', c_uint32, 1),
                ('rsvd1', c_uint32, 1),
                ('ZF', c_uint32, 1),
                ('SF', c_uint32, 1),
                ('TF', c_uint32, 1),
                ('IF', c_uint32, 1),
                ('DF', c_uint32, 1),
                ('OF', c_uint32, 1),
                ('IOPL', c_uint32, 2),
                ('NT', c_uint32, 1),
                ('rsvd2', c_uint32, 1),
                ('RF', c_uint32, 1),
                ('VM', c_uint32, 1),
                ('AC', c_uint32, 1),
                ('VIF', c_uint32, 1),
                ('VIP', c_uint32, 1),
                ('ID', c_uint32, 1),
                ('rsvd3', c_uint32, 10)]

    def __init__(self):
        self.one = 1

assert sizeof(RegEflags) == 4

class RegCr0(Structure):
    _pack_ = 1
    _fields_ = [('PE', c_uint32, 1),
                ('MP', c_uint32, 1),
                ('EM', c_uint32, 1),
                ('TS', c_uint32, 1),
                ('ET', c_uint32, 1),
                ('NE', c_uint32, 1),
                ('rsvd0', c_uint32, 10),
                ('WP', c_uint32, 1),
                ('rsvd1', c_uint32, 1),
                ('AM', c_uint32, 1),
                ('rsvd2', c_uint32, 10),
                ('NW', c_uint32, 1),
                ('CD', c_uint32, 1),
                ('PG', c_uint32, 1)]

assert sizeof(RegCr0) == 4

class UnionRegCr0(Union):
    _fields_ = [("reg", RegCr0), ("val", c_uint32)]


class RegEfer(Structure):
    _fields_ = [('SCE', c_uint32, 1),
                ('rsvd0', c_uint32, 7),
                ('LME', c_uint32, 1),
                ('rsvd1', c_uint32, 1),
                ('LMA', c_uint32, 1),
                ('NXE', c_uint32, 1),
                ('SVME', c_uint32, 1),
                ('rsvd2', c_uint32, 19)]

assert sizeof(RegEfer) == 4

class UnionRegEfer(Union):
    _fields_ = [("reg", RegEfer), ("val", c_uint32)]

class TssDesc32(GdtEntry):
    pass

class TssDesc64(TssDesc32):
    _pack_ = 1
    _fields_ = [('base32_63', c_uint32),
                ('rsvd', c_uint32)]

    def __init__(self, base = 0, limit = 0, type = 0, s = 0, dpl = 0, p = 0, l = 0, db = 0, g = 0):
        self.base32_63 = (base >> 32) & 0xffffffff
        TssDesc32.__init__(self, base & 0xffffffff, limit, type, s, dpl, p, l, db, g)

    @property
    def base(self):
        return TssDesc32.base(self) | (self.base32_63 << 32)

class Memory(bytearray):
    def allocate(self, size, alignment = 1):
        addr = (len(self) + alignment - 1) // alignment * alignment
        self.extend(b'\x00' * (addr + size - len(self)))
        return addr

    def write(self, addr, content):
        assert addr + len(content) <= len(self)
        self[addr:addr + len(content)] = content

    def read(self, addr, size):
        assert addr + size <= len(self)
        return self[addr:addr + size]

class VMState(object):
    def __init__(self, boot_mode: ARCH = ARCH.X86):
        self.memory = Memory()
        self.vmsa = struct_vmcb_save_area()
        assert boot_mode in (ARCH.X86, ARCH.X64), 'Unsupported arch: %s' % arch
        cr0 = UnionRegCr0()
        cr0.reg.PE = 1
        self.vmsa.g_pat = PAT_RESET_VAL
        self.vmsa.cr0 = cr0.val
        self.boot_mode = boot_mode
        efer = UnionRegEfer()
        efer.reg.SVME = 1
        if self.boot_mode == ARCH.X64:
            efer.reg.SCE = 1
            efer.reg.LME = 1
            efer.reg.LMA = 1
            efer.reg.NXE = 1
        self.vmsa.efer = efer.val

    def setup_paging(self):
        '''
        Setup an identity mapping (VA == PA) with full accesses.
        '''
        addr = self.memory.allocate(0)
        if self.boot_mode != ARCH.X64:
            return addr
        print("paging")
        efer = UnionRegEfer()
        efer.val = self.vmsa.efer
        cr0 = UnionRegCr0()
        cr0.val = self.vmsa.cr0
        cr4 = UnionRegCr4()
        cr4.val = self.vmsa.cr4
        
        assert cr0.reg.PG == 0
        assert efer.reg.LMA  == 1
        # allocate a PML4 and a PDPT
        p4d_addr = self.memory.allocate(PGSIZE, PGSIZE)
        pgd_addr = self.memory.allocate(PGSIZE, PGSIZE)
        # make the first PML4 entry point to the PDPT
        p4d = p4d_t.from_buffer(self.memory, p4d_addr)
        p4d.val = pgd_addr
        p4d.val |= _PAGE_RW_U_P
        p4d.val |= _PAGE_ENCRYPTED
        # setup identity mapping for [0, 512GB)
        for i in range(PGSIZE // sizeof(pgd_t)):
            pgd = pgd_t.from_buffer(self.memory, pgd_addr + i * sizeof(pgd_t))
            pgd.val = (i << 30)
            pgd.val |= _PAGE_ENCRYPTED
            pgd.val |= _PAGE_RW_U_P
            pgd.val |= _PAGE_PAGE_PSE
        cr4.reg.PAE = 1
        # setup cr3
        self.vmsa.cr3 = p4d_addr | _PAGE_ENCRYPTED
        # enable large page support
        cr4.reg.PSE = 1
        # turn on paging
        cr0.reg.PG = 1
        self.vmsa.cr0 = cr0.val
        self.vmsa.cr4 = cr4.val
        self.vmsa.efer = efer.val
        print("%x"%self.vmsa.efer)
        return addr
        

    def load_seg(self, vmcb_seg: struct_vmcb_seg, selector: int):
        '''
        Load the segment register and update its cache accordingly.
        '''
        assert (selector & 0b100) == 0, 'LDT is not supported yet'
        assert selector + sizeof(struct_desc_struct) - 1 <= self.vmsa.gdtr.limit
        desc_addr = self.vmsa.gdtr.base + (selector & ~0x7)
        desc = GdtEntry.from_buffer(self.memory, desc_addr)
        vmcb_seg.base = desc.base
        vmcb_seg.selector = selector
        vmcb_seg.limit = desc.limit if not desc.g else (desc.limit * PGSIZE + PGSIZE - 1)
        vmcb_seg.attrib = desc.attribute

    def setup_gdt(self):
        '''
        Setup the Global Descriptor Table (GDT) using flat memory model.
        The constructed GDT will be like [NULL, KT, UT, KD, UD, TSS], and
        all the segment registers are initialized to refer to KT/KD.
        If you wish to setup a customized GDT, please do it yourself.
        '''
        assert self.vmsa.gdtr.base == 0
        assert self.vmsa.gdtr.limit == 0
        start_addr = self.memory.allocate(0)
        # create a task state segment
        efer = UnionRegEfer()
        efer.val = self.vmsa.efer
        long_mode = efer.reg.LMA
        # GDT always starts with a NULL descriptor

        KERNEL_PRIV = 0
        USER_PRIV = 3
        NOT_TSS =  1
        PRESENT = 1
        USE_PAGE = 1
        CODE_TYPE = 0b1011
        DATA_TYPE = 0b0011

        gdt = [struct_desc_struct(),  # NULL
               GdtEntry(0, 0xfffff, CODE_TYPE, NOT_TSS, KERNEL_PRIV,
                              PRESENT, long_mode, 1 - long_mode, USE_PAGE),
               GdtEntry(0, 0xfffff, CODE_TYPE, NOT_TSS, USER_PRIV,
                              PRESENT, long_mode, 1 - long_mode, USE_PAGE),
               GdtEntry(0, 0xfffff, DATA_TYPE, NOT_TSS, KERNEL_PRIV,
                              PRESENT, 0, 1, USE_PAGE),
               GdtEntry(0, 0xfffff, DATA_TYPE, NOT_TSS, USER_PRIV,
                              PRESENT, 0, 1, USE_PAGE), ]
        """
        tss_size = 104
        tss_addr = self.memory.allocate(tss_size)
        if long_mode:
            print("long")
            gdt.append(TssDesc64(tss_addr, tss_size - 1, CODE_TYPE, ~NOT_TSS, KERNEL_PRIV, PRESENT, 0, 0, 0))
        else:
            gdt.append(TssDesc32(tss_addr, tss_size - 1, CODE_TYPE, ~NOT_TSS, KERNEL_PRIV, PRESENT, 0, 0, 0))
        """
        # allocate GDT from the memory
        gdt_size = sum([sizeof(desc) for desc in gdt])
        gdt_addr = self.memory.allocate(gdt_size)
        # initialize the GDT layout accordingly
        self.memory.write(gdt_addr, b''.join([bytearray(desc) for desc in gdt]))
        # update gdtr to point to the GDT in memory
        self.vmsa.gdtr.base = gdt_addr
        self.vmsa.gdtr.limit = gdt_size - 1
        # update segment registers
        self.load_seg(self.vmsa.cs, 0x8)
        self.load_seg(self.vmsa.ds, 0x18)
        self.load_seg(self.vmsa.es, 0x18)
        self.load_seg(self.vmsa.ss, 0x18)
        #self.load_seg(self.vmsa.tr, 0x28)
        return start_addr
