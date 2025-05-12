# launch/cartographer_occupancy.launch.py

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from antrobot_ros.utils import load_node_params

def generate_launch_description():
    # declare namespace so we get the right YAML params
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace for the robot instance'
    )
    ns = LaunchConfiguration('namespace')

    # load your resolution & publish_period from antrobot_params.yaml
    pkg_share = get_package_share_directory('antrobot_ros')
    cfg_path = os.path.join(pkg_share, 'config', 'antrobot_params.yaml')
    carto_params = load_node_params(cfg_path, 'cartographer')

    occ_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': False}],
        arguments=[
            '-resolution',         str(carto_params['resolution']),
            '-publish_period_sec', str(carto_params['publish_period_sec']),
        ],
        remappings=[
            # publish occupancy on the *global* /map:
            ('occupancy_grid', '/map'),
        ],
    )

    return LaunchDescription([
        namespace_arg,
        occ_node,
    ])
