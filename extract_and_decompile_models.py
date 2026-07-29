import struct, zlib, marshal, dis

pyz_path = r"build/POS_LaRuta_Este/PYZ-00.pyz"
with open(pyz_path, "rb") as f:
    f.seek(8)
    toc_pos = struct.unpack("!I", f.read(4))[0]
    f.seek(toc_pos)
    toc = marshal.load(f)
    
    for name, info in toc:
        if name == "models":
            ispkg, pos, length = info
            f.seek(pos)
            compressed = f.read(length)
            decompressed = zlib.decompress(compressed)
            code_obj = marshal.loads(decompressed)
            print("Successfully extracted models code_obj! Name:", code_obj.co_name)
            
            # Print all classes and method names in code_obj
            print("\nClasses and methods in models.py:")
            for const in code_obj.co_consts:
                if hasattr(const, "co_name"):
                    print(f"  Class: {const.co_name}")
                    for inner in getattr(const, "co_consts", []):
                        if hasattr(inner, "co_name"):
                            print(f"    Method: {inner.co_name}")
