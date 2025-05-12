# Copyright (C) 2025 Dan Novischi.
# This software may be modified and distributed under the terms of the
# GNU Lesser General Public License v3 or any later version.

import os, tempfile, yaml
from launch               import LaunchDescription 
from launch.actions       import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction, OpaqueFunction, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration
from launch_ros.actions   import PushRosNamespace
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def _rewrite_yaml(context):
        ns   = context.launch_configurations['namespace']
        src  = context.launch_configurations['params_file']

        with open(src, 'r') as f:
            data = yaml.safe_load(f)

        # naïve replacement – customise as needed
        def rewrite(v):
            if isinstance(v, str):
                return v.replace('antrobot1', ns) if ns else v
            if isinstance(v, list):
                return [rewrite(x) for x in v]
            if isinstance(v, dict):
                return {k: rewrite(x) for k, x in v.items()}
            return v
        new_yaml = rewrite(data)

        tmpdir   = tempfile.mkdtemp(prefix='nav2_params_')
        out      = os.path.join(tmpdir, 'nav2_rewritten.yaml')
        with open(out, 'w') as f:
            yaml.safe_dump(new_yaml, f)

        # <-- **THIS** is the bit that was missing
        return [SetLaunchConfiguration('nav2_rewritten_yaml', out)]

def generate_launch_description():
    # CLI args
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if true'
    )
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('antrobot_ros'),
            'config',
            'nav2_params.yaml'
        ]),
        description='Full path to the ROS2 parameters file to use'
    )
    map_yaml_arg = DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution([
            FindPackageShare('antrobot_ros'),
            'maps',
            'map.yaml'
        ]),
        description='Full path to map yaml file to load'
    )
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Top-level namespace for all Nav2 nodes'
    )

    rewrite_action = OpaqueFunction(function=_rewrite_yaml)

    # 1) The real Nav2 bringup (namespacing is handled at the top level)
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            ])
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file':  LaunchConfiguration('nav2_rewritten_yaml'),
            'map':          LaunchConfiguration('map'),
            # no 'namespace' here—your top‐level launch will PushRosNamespace
        }.items()
    )

    # 2) Relay global /tf → <namespace>/tf
    tf_relay = Node(
        package='topic_tools',
        executable='relay',
        name='tf_relay',
        output='screen',
        arguments=['/tf', 'tf']
    )

    # 3) Relay global /tf_static → <namespace>/tf_static
    tf_static_relay = Node(
        package='topic_tools',
        executable='relay',
        name='tf_static_relay',
        output='screen',
        arguments=['/tf_static', 'tf_static']
    )

    return LaunchDescription([
        # declare args
        use_sim_time_arg,
        params_file_arg,
        map_yaml_arg,
        namespace_arg,
        rewrite_action,
        # bring up Nav2
        nav2_bringup,

        # these relays subscribe to the *global* /tf and /tf_static
        # and re-publish on the *relative* tf/tf_static topics in your namespace
        tf_relay,
        tf_static_relay,
    ])
