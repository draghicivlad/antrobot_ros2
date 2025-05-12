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

import os, yaml, tempfile, shutil
from ament_index_python.packages import get_package_share_directory
from launch.actions import OpaqueFunction

def _rewrite_params_in_place(context):
    ns  = context.launch_configurations.get('namespace', '')
    if not ns:                             # nothing to rewrite
        return []

    pkg_share = get_package_share_directory('antrobot_ros')
    yaml_path = os.path.join(pkg_share, 'config', 'antrobot_params.yaml')

    # keep an untouched copy so a second robot can restore it later
    backup = yaml_path + '.orig'
    if not os.path.exists(backup):
        shutil.copy2(yaml_path, backup)

    with open(backup, 'r') as f:
        data = yaml.safe_load(f)

    # --- do your replacements -----------------------------------------
    def rewrite(v):
        if isinstance(v, str):
            return v.replace('antrobot1', ns)
        if isinstance(v, list):
            return [rewrite(x) for x in v]
        if isinstance(v, dict):
            return {k: rewrite(x) for k, x in v.items()}
        return v
    data = rewrite(data)

    with open(yaml_path, 'w') as f:          # overwrite *the* file
        yaml.safe_dump(data, f)

    # nothing else to return – all other launch files will read the same path
    return []

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
    cartographer_launch_arg = DeclareLaunchArgument('launch_cartographer', default_value='true', description='Launch cartographer')
    nav2_launch_arg = DeclareLaunchArgument('launch_nav2', default_value='true', description='Launch nav2')

    rewrite_antrobot_yaml = OpaqueFunction(function=_rewrite_params_in_place)

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

    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'cartographer.launch.py')
        ),
        condition=
            IfCondition(LaunchConfiguration('do_mapping')),
        launch_arguments={}.items()
    )

    cartographer_occ_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(FindPackageShare('antrobot_ros').find('antrobot_ros'), 'launch', 'cartographer_occupancy.launch.py')
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
        cartographer_launch,
        cartographer_occ_launch,
        nav2_launch,
    ])

    return LaunchDescription([
        # still declare all your args at the top…
        rewrite_antrobot_yaml,
        namespace_launch_arg,
        mapping_arg,
        rdrive_launch_arg,
        rplidar_launch_arg,
        tf_static_link_launch_arg,
        cartographer_launch_arg,
        nav2_launch_arg,
        namespaced_group,
        
    ])
