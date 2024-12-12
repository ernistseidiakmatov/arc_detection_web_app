import ctypes



def collect_data(num_samples, signal_type, save_dir):
    try: 
        class SignalData(ctypes.Structure):
            _fields_ = [
                ("data", ctypes.c_char_p),
                ("size", ctypes.c_size_t),
            ]
        collector_lib = ctypes.CDLL('./utils/lib_collector.so')
        collector_lib.collect_and_save.argtypes = [
            ctypes.c_int,        # num_samples
            ctypes.c_char_p,     # signal_type
            ctypes.c_char_p,     # save_dir
        ]
        collector_lib.collect_and_save.restype = SignalData

        collector_lib.free_signal.argtypes = [ctypes.POINTER(SignalData)]
        collector_lib.free_signal.restype = None

        result = collector_lib.collect_and_save(
            num_samples,
            signal_type.encode('utf-8'),
            save_dir.encode('utf-8')
        )

        file_name = result.data.decode('utf-8')
        print(file_name)
        collector_lib.free_signal(ctypes.byref(result))
        return file_name
    except:
        return "Error occurred during data collection"