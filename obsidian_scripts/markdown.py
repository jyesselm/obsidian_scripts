
def extract_metadata_from_md_file(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    text = "".join(lines)
    sections = text.split("---")
    lines = sections[1].split("\n")
    metadata = {}
    for l in lines:
        spl = l.split(":")
        if len(spl) < 2:
            continue
        key, value = spl
        key = key.strip()
        value = value.strip()
        metadata[key] = value
    return metadata

def remove_metadata_from_md_content(content):
    pass