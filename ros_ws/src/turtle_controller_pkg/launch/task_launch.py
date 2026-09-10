import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('turtle_controller_pkg'),
        'config',
        'params.yaml'
    )

    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim'
        ),
        Node(
            package='turtle_controller_pkg',
            executable='go_to_goal_node',
            name='go_to_goal',
            parameters=[config]
        ),
        Node(
            package='turtle_controller_pkg',
            executable='delayed_node',
            name='delayed_client'
        )
    ])