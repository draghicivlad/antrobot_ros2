# Copyright (C) 2025 Dan Novischi.
# This software may be modified and distributed under the terms of the
# GNU Lesser General Public License v3 or any later version.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from antrobot_ros.utils import load_node_params  

def generate_launch_description():
    # Robot namespace (e.g. "antrobot1")
    robot_namespace_arg = DeclareLaunchArgument(
        'namespace', default_value='',
        description='Namespace for the robot instance'
    )

    # Load transforms list
    config_file = os.path.join(
        get_package_share_directory('antrobot_ros'),
        'config',
        'antrobot_params.yaml'
    )
    tf_params = load_node_params(config_file, 'tf_static')
    transforms = tf_params['transforms']

    # One static_transform_publisher per link, prefixing frames with "<ns>_"
    tf_nodes = []
    for t in transforms:
        ns = LaunchConfiguration('namespace')
        parent = [ns, TextSubstitution(text='_' + t['parent_frame'])]
        child  = [ns, TextSubstitution(text='_' + t['child_frame'])]

        tf_nodes.append(Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name=f"tf_static_{t['parent_frame']}_to_{t['child_frame']}",
            output='screen',
            arguments=[
                '--x', str(t['translation'][0]),
                '--y', str(t['translation'][1]),
                '--z', str(t['translation'][2]),
                '--roll',  str(t['rotation'][0]),
                '--pitch', str(t['rotation'][1]),
                '--yaw',   str(t['rotation'][2]),
                '--frame-id',       parent,
                '--child-frame-id', child,
            ],
            remappings=[('tf_static', 'tf_static')],
        ))

    return LaunchDescription([robot_namespace_arg] + tf_nodes)
