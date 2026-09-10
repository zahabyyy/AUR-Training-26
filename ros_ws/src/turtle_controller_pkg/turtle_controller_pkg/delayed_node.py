import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
import time

class DelayedClient(Node):
    def __init__(self):
        super().__init__('delayed_client')
        self.client = self.create_client(SetBool, 'toggle_movement')
        
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for toggle_movement service...')
            
        self.get_logger().info('Service found. Waiting 3 seconds...')
        time.sleep(3.0)
        
        self.req = SetBool.Request()
        self.req.data = True
        self.future = self.client.call_async(self.req)
        self.get_logger().info('Start request sent.')

def main(args=None):
    rclpy.init(args=args)
    node = DelayedClient()
    rclpy.spin_until_future_complete(node, node.future)
    rclpy.shutdown()

if __name__ == '__main__':
    main()