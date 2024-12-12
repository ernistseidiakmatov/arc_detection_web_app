import os
import math
import shutil

# def_dir = "/home/netvision/data_collector/arc_detection_web_app/utils"

def get_dir_size(dir):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it is a symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return convert_size(total_size)

def get_available_disk_space(dir):
    total, used, free = shutil.disk_usage(dir)
    return convert_size(free)

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"