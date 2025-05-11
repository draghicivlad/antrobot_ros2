# Copyright (C) 2025 Dan Novischi. All rights reserved.
# This software may be modified and distributed under the terms of the
# GNU Lesser General Public License v3 or any later version.
import os
import re
import platform
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    hostname = platform.node()
    
    namespace_launch_arg = DeclareLaunchArgument('namespace', default_value=hostname, description='Namespace for the robot')
    mapping_arg = DeclareLaunchArgument(
        'do_mapping', default_value='true',
        description='Set to true on the one robot that will build the map'
    )
    rdrive_launch_arg = DeclareLaunchArgument('launch_rdrive', default_value='true', description='Launch rdrive')
    rplidar_launch_arg = DeclareLaunchArgument('launch_rplidar', default_value='true', description='Launch rplidar')
    tf_static_link_launch_arg = DeclareLaunchArgument('launch_tf_static_link', default_value='true', description='Launch tf_static_link')
    laserscan_to_pointcloud_launch_arg = DeclareLaunchArgument('launch_laserscan_to_pointcloud', default_value='false', description='Launch laserscan_to_pointcloud')
    kiss_icp_launch_arg = DeclareLaunchArgument('launch_kiss_icp', default_value='false', description='Launch kiss_icp')
    cartographer_launch_arg = DeclareLaunchArgument('launch_cartographer', default_value='true', description='Launch cartographer')
    nav2_launch_arg = DeclareLaunchArgument('launch_nav2', default_value='true', description='Launch nav2')

    # Include launch files conditionally
    rdrive_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'rdrive.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_rdrive')),
        launch_arguments={}.items()
    )

    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'rplidar.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_rplidar')),
        launch_arguments={}.items()
    )
    
    tf_static_link_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'tf_static_link.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_tf_static_link')),
    )

    laserscan_to_pointcloud_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'laserscan_to_pointcloud.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_laserscan_to_pointcloud')),
        launch_arguments={}.items()
    )

    kiss_icp_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'kiss_icp.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_kiss_icp')),
        launch_arguments={}.items()
    )

    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'cartographer.launch.py')
        ),
        condition=
            IfCondition(LaunchConfiguration('do_mapping')),
        launch_arguments={}.items()
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'nav2.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('launch_nav2')),
        launch_arguments={}.items()
    )

    namespaced_group = GroupAction([
        PushRosNamespace(LaunchConfiguration('namespace')),
        tf_static_link_launch,
        rdrive_launch,
        rplidar_launch,
        laserscan_to_pointcloud_launch,
        kiss_icp_launch,
        cartographer_launch,
        nav2_launch,
    ])

    return LaunchDescription([
        # still declare all your args at the top…
        namespace_launch_arg,
        mapping_arg,
        rdrive_launch_arg,
        rplidar_launch_arg,
        tf_static_link_launch_arg,
        laserscan_to_pointcloud_launch_arg,
        kiss_icp_launch_arg,
        cartographer_launch_arg,
        nav2_launch_arg,
        namespaced_group,
    ])
