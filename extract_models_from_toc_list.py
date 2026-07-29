import struct, zlib, marshal

pyz_path = r"build/POS_LaRuta_Este/PYZ-00.pyz"
with open(pyz_path, "rb") as f:
    f.seek(8)
    toc_pos = struct.unpack("!I", f.read(4))[0]
    f.seek(toc_pos)
    toc = marshal.load(f)
    print("TOC type:", type(toc), "length:", len(toc))
    
    for item in toc:
        name = item[0]
        if name == "models":
            print("Found models item:", item)
            pos = item[2]
            length = item[3]
            f.seek(pos)
            compressed = f.read(length)
            decompressed = zlib.decompress(compressed)
            code_obj = marshal.loads(decompressed)
            print("Code object loaded successfully! Name:", code_obj.co_name)
            # Inspect sub code objects (classes)
            for const in code_obj.co_consts:
                if hasattr(const, "co_name"):
                    print("  Found inner class/func:", const.co_name)
