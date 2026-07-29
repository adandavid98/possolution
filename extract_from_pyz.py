import os, struct, zlib, marshal

pyz_path = r"build/POS_LaRuta_Este/PYZ-00.pyz"
if os.path.exists(pyz_path):
    with open(pyz_path, "rb") as f:
        magic = f.read(4)
        print("Magic:", magic)
        # Read PYZ header
        toc_offset = struct.unpack("!I", f.read(4))[0]
        f.seek(toc_offset)
        toc = marshal.load(f)
        print("TOC entries count:", len(toc))
        if "models" in toc:
            print("Found 'models' in PYZ TOC!")
            entry = toc["models"]
            ispkg, pos, length = entry
            f.seek(pos)
            compressed = f.read(length)
            decompressed = zlib.decompress(compressed)
            with open("extracted_models.pyc", "wb") as out:
                out.write(decompressed)
            print("Extracted models.pyc! Length:", len(decompressed))
