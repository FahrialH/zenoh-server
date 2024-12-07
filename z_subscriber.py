import zenoh
from ecg_server import signal_listener

if __name__ == "__main__":
    print('[INFO] Open zenoh session for processing signal...')
    key = 'demo/fs/ecg/*'
    zenoh.init_log_from_env_or("error")
    conf = zenoh.Config()
    z = zenoh.open(conf)
    sub = z.declare_subscriber(key, signal_listener)