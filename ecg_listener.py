import zenoh
import json
from json import JSONEncoder
import base64
import zlib as z
import numpy as np
import neurokit2 as nk
import pywt
import cv2
from requests import session

sample_rate = 512
duration = 30
before_rpeak = int(0.32*sample_rate)
after_rpeak = int(0.48*sample_rate)
segment_size = before_rpeak + after_rpeak + 1
    
img_size = 128
output_size = (img_size, img_size)
n_scales = 128
n_choices = 9
scales = np.arange(1, n_scales+1)
waveletname = 'gaus1'

np.set_printoptions(precision=8)

# When a client (smartphone) put (post) ECG signal to the server,
# the callback signal_listener will be called,
# this function will process and manage ECG data
def signal_listener(sample):
    # read key string
    keyString = str(sample.key_expr)
    #print(keyString)
    
    # read ECG signal from the payload
    dt = np.dtype(np.float32).newbyteorder('>')
    payload = bytes(sample.payload) #[CHANGE]bytes to match ecg_put.py
    data = np.frombuffer(payload, dtype=dt)
    data_size = len(data)
    # print(data_size)
    
    # clean and find R-Peaks
    data = nk.ecg_clean(data, sampling_rate=sample_rate)
    processed_data, info = nk.ecg_process(data, sampling_rate=sample_rate)
    rpeaks = np.nonzero(np.array(processed_data['ECG_R_Peaks']))[0]
    n_rpeaks = len(rpeaks)
    #print(rpeaks)
    
    # ECG signal will be stored in the folder 'ecg'
    # CWT will be stored in the folder 'cwt' 
    keyString = keyString.replace('ecg', 'cwt')
    # print(keyString)
    
    # get 9 CWT segments (n_choices) after the second R-Peak (offset=2) 
    offset = 2
    for i in range(min(n_rpeaks-2, n_choices)):
        # extract segment
        segment = data[rpeaks[i+offset]-before_rpeak:rpeaks[i+offset]+after_rpeak+1]
        # calculate cwt
        segment, _ = pywt.cwt(segment, scales, waveletname)
        # resize and flatten
        segment = cv2.resize(segment, output_size).flatten().astype(np.float32)
        # convert to byte array
        segment = segment.tobytes()
        # put in the database of Zenoh, with postfix is the order identity of the segment (str(i)).
        # request GET on smartphone using this key string you can get the corresponding CWT segment data.
        z.put(keyString + '_' + str(i), segment)
        print('Put: ', keyString + '_' + str(i))
    print('-'*120)
#-----------------------------------------------------
if __name__ == "__main__":
    print('[INFO] Open zenoh session for processing signal...')
    key = 'demo/fs/ecg/test_signal'  # CHANGE PATH FOR TESTING
    zenoh.init_log_from_env_or("error")
    conf = zenoh.Config()
    session = zenoh.open(conf)

    try:
        sub = session.declare_subscriber(key, signal_listener)
        # Keep the program running until interrupted
        while True:
            pass  # You can replace this with any other logic if needed
    except KeyboardInterrupt:
        print('[INFO] Keyboard interrupt received. Closing session...')
    finally:
        session.close()
        print('[INFO] Zenoh session closed.')