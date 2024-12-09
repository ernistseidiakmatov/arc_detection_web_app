from utils.storage import *



dir = "D:"

size_in_bytes = get_dir_size(dir)
print(f"Total size of '{dir}' is: {size_in_bytes} bytes")

print("Available size: ", get_available_disk_space(dir))