#pubslish sample test
import zenoh
import numpy as np

def send_data():
    return np.random.rand(512).astype(np.float32)

if __name__ == "__main__":
    session = zenoh.open(zenoh.Config())
    key = "demo/fs/ecg/test_signal"
    pub = session.declare_publisher(key)

    t = send_data()
    buf = f"{t}"
    print(f"Published mock data to ('{key}':'{buf}')")
    session.put(key, t.tobytes())