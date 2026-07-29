import struct, zlib, marshal

pyz_path = r"build/POS_LaRuta_Este/PYZ-00.pyz"
with open(pyz_path, "rb") as f:
    f.seek(8) # Skip 8 bytes header
    toc_pos = struct.unpack("!I", f.read(4))[0]
    f.seek(toc_pos)
    toc = marshal.load(f)
    if "models" in toc:
        entry = toc["models"]
        print("models entry in TOC:", entry)
        pos = entry[1]
        length = entry[2]
        f.seek(pos)
        compressed = f.read(length)
        decompressed = zlib.decompress(compressed)
        code_obj = marshal.loads(decompressed)
        print("code_obj loaded successfully! Name:", code_obj.co_name)
        with open("extracted_models.pyc", "wb") as out:
            out.write(decompressed)
        print("Saved extracted_models.pyc!")
    else:
        print("models not in TOC keys. Sample keys:", list(toc.keys())[:20])
