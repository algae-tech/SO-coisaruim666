import struct

BLOCK = 1024
INODE_SIZE = 64
DIRENT_SIZE = 16  # 2 byte inum + 14 char name (magic 0x2468)

class MinixFS:
    def __init__(self, data, part_offset):
        self.data = data
        self.base = part_offset
        sb = data[self.base+1024:self.base+1024+24]
        (self.s_ninodes, self.s_nzones, self.s_imap, self.s_zmap, self.s_firstdata,
         self.s_logzone, self.s_maxsize, self.s_magic, self.s_state, self.s_zones) = \
            struct.unpack('<HHHHHHIHHI', sb)
        assert self.s_magic == 0x2468, "esperado Minix V2 fs, 14-char filenames"
        self.inode_table_block = 2 + self.s_imap + self.s_zmap

    def read_block(self, blocknum):
        off = self.base + blocknum * BLOCK
        return self.data[off:off+BLOCK]

    def read_inode(self, inum):
        # inum is 1-based
        byte_off = (inum - 1) * INODE_SIZE
        block = self.inode_table_block + byte_off // BLOCK
        off_in_block = byte_off % BLOCK
        raw = self.read_block(block)[off_in_block:off_in_block+INODE_SIZE]
        (i_mode, i_nlinks, i_uid, i_gid, i_size, i_atime, i_mtime, i_ctime) = \
            struct.unpack('<HHHHIIII', raw[:24])
        zones = struct.unpack('<10I', raw[24:64])
        return dict(mode=i_mode, nlinks=i_nlinks, size=i_size, zones=zones)

    def _collect_zones(self, zones, needed_zones):
        """expand direct+indirect+double-indirect zone list to a flat list of data zone numbers"""
        result = []
        # 7 direct
        for z in zones[0:7]:
            result.append(z)
            if len(result) >= needed_zones:
                return result
        # single indirect (zones[7]): block full of 256 zone numbers
        if zones[7]:
            ind = self.read_block(zones[7])
            ptrs = struct.unpack('<256I', ind)
            for z in ptrs:
                result.append(z)
                if len(result) >= needed_zones:
                    return result
        # double indirect (zones[8])
        if zones[8]:
            ind = self.read_block(zones[8])
            ptrs1 = struct.unpack('<256I', ind)
            for p1 in ptrs1:
                if not p1:
                    continue
                ind2 = self.read_block(p1)
                ptrs2 = struct.unpack('<256I', ind2)
                for z in ptrs2:
                    result.append(z)
                    if len(result) >= needed_zones:
                        return result
        return result

    def read_file(self, inode):
        size = inode['size']
        needed_zones = (size + BLOCK - 1) // BLOCK
        zonelist = self._collect_zones(inode['zones'], needed_zones)
        out = b''
        for z in zonelist[:needed_zones]:
            out += self.read_block(z) if z else (b'\x00'*BLOCK)
        return out[:size]

    def list_dir(self, inode):
        raw = self.read_file(inode)
        entries = {}
        for i in range(0, len(raw), DIRENT_SIZE):
            chunk = raw[i:i+DIRENT_SIZE]
            if len(chunk) < DIRENT_SIZE:
                break
            inum = struct.unpack('<H', chunk[0:2])[0]
            name = chunk[2:16].split(b'\x00')[0].decode('ascii', errors='replace')
            if inum != 0 and name not in ('', '.', '..'):
                entries[name] = inum
        return entries

    def resolve_path(self, path):
        """path relative to filesystem root, e.g. 'src/kernel/proc.c'"""
        parts = [p for p in path.split('/') if p]
        cur_inode_num = 1  # root
        cur_inode = self.read_inode(cur_inode_num)
        for i, part in enumerate(parts):
            entries = self.list_dir(cur_inode)
            if part not in entries:
                raise FileNotFoundError(f"'{part}' nao encontrado (path={path}); disponiveis: {list(entries.keys())}")
            cur_inode_num = entries[part]
            cur_inode = self.read_inode(cur_inode_num)
        return cur_inode

    def read_path(self, path):
        inode = self.resolve_path(path)
        return self.read_file(inode)
