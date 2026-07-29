import dis, marshal, zlib, struct

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
            decompressed = zlib.decompress(f.read(length))
            code_obj = marshal.loads(decompressed)
            
            # Print co_consts strings to extract SQL queries
            print("Extracted SQL strings from models.py:")
            for const in code_obj.co_consts:
                if isinstance(const, str) and ("SELECT" in const or "INSERT" in const or "UPDATE" in const or "DELETE" in const):
                    print("  SQL:", repr(const))
                if hasattr(const, "co_consts"):
                    for inner in const.co_consts:
                        if isinstance(inner, str) and ("SELECT" in inner or "INSERT" in inner or "UPDATE" in inner or "DELETE" in inner):
                            print(f"  {const.co_name} SQL:", repr(inner))
