import zenoh
import time
import cv2
import numpy as np

#listener debugging. make sure incoming data is readable
def subscriber_callback(sample):
    """
    Callback function to receive and visualize ECG data. 
    //later build put function to send sample data to zenoh//
    """
    #DATA HANDLING
    #decode payload into original format
    payload = bytes(sample.payload)
    
    data = np.frombuffer(payload, dtype=np.float32)

    #reshape data to match expected image size (from ecg_listener)
    img_size = 128
    segment = data.reshape(img_size, img_size)

    #display segment data as image
    print(f"Received data on {sample.key_expr}. Displaying... ")
    cv2.imshow("Segment", segment)
    cv2.waitkey(1000) #show for 1 second
    cv2.destroyAllWindows()

def main():
    """
    Main Function to start subscriber
    """
    zenoh.init_log_from_env_or("error")
    conf = zenoh.Config()
    z = zenoh.open(conf)

    # Subscribe to cwt path
    resource_path = "demo/fs/ecg/test_signal"
    sub = z.declare_subscriber(resource_path, subscriber_callback)
    print(f"[INFO] Subscribed to {resource_path}")

    # keep subscriber active
    try:
        input("Press Enter to terminate subscriber \n")
    finally:
        sub.undeclare()
        z.close()

if __name__ == "__main__":
    main()
