import os 
import shutil
import zipfile
from datetime import datetime

def check_save_dir(save_dir):
    arc_dir = os.path.join(save_dir, 'arc')
    non_arc_dir = os.path.join(save_dir, 'non-arc')

    if not (os.path.isdir(arc_dir) and os.path.isdir(non_arc_dir)):
        raise ValueError("Both paths must be valid directories.")

    is_arc_dir_not_empty = len(os.listdir(arc_dir)) > 0
    is_non_arc_dir_not_empty = len(os.listdir(non_arc_dir)) > 0

    if is_arc_dir_not_empty or is_non_arc_dir_not_empty:
        return True
    else:
        return False


def zip_folder(folder_path, output_zip_path):
    try:
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.relpath(file_path, start=folder_path))
        return "success"
    except Exception as e:
        print(e)
        return "error"

def transfer_data(save_dir):
    is_dataset_avl = check_save_dir(save_dir)

    if is_dataset_avl:
        media_dir = "/media/netvision/"
        usb = os.listdir(media_dir)
        if usb:
            usb_dir = os.path.join(media_dir, usb[0])
            curr_date = datetime.now()
            curr_date = curr_date.strftime("%Y-%m-%d_%H-%M-%S")
            usb_path = os.path.join(usb_dir, (str(curr_date) + "_dataset.zip"))
            r = zip_folder(save_dir, usb_path)
            print(r)
            return "Transfered to USB"
        else: 
            return "No USB found"
    else:
        return "No dataset found"