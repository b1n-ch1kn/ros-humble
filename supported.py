import pandas as pd
import yaml
import os

# get the file's current directory
cwd = os.path.dirname(os.path.realpath(__file__)) + "/"

PLATFORM = 'linux_64'
file = cwd + 'vinca_' + PLATFORM + '.yaml'


# load a text file of ROS2 packages query them against a list of supported packages

# load yaml file as raw text to get comments
with open(file, 'r') as f:
    # read lines
    vinca_yaml = f.read().splitlines()
    
    # find lines below 'packages_selected_from_deps:'
    # and above 'patch_dir:'
    # packages = data[data.index('packages_selected_from_deps:')+1:]
    ros2_packages = vinca_yaml[vinca_yaml.index('packages_select_by_deps:')+1:vinca_yaml.index('patch_dir: patch')]

    # remove blank lines
    ros2_packages = [x for x in ros2_packages if x]

    """
    packages are in the format:
      # only subset of packages to reduce maintainer load

      # - ros_workspace
      # - ros_environment
    """

    # get lines with `  - ` at the start or `  # - ` at the start
    ros2_packages = [x for x in ros2_packages if x.startswith('  - ') or x.startswith('  # - ')]
    # remove `  - ` from the start of each line
    ros2_packages = [x.replace('  - ', '') for x in ros2_packages]
    # remove `  # - ` from the start of each line
    ros2_packages = [x.replace('  # - ', '') for x in ros2_packages]
    # replace `_` with `-` in each line
    ros2_packages = [x.replace('_', '-') for x in ros2_packages]
    # add `ros-humble-` to the start of each line
    ros2_packages = ['ros-humble-' + x for x in ros2_packages]
    # remove duplicates
    ros2_packages = list(dict.fromkeys(ros2_packages))


# load csv file of supported packages
avail = pd.read_csv(cwd + 'table.csv', delimiter='|')

"""
each line is in the format:
| Package |  linux-64 | win-64 | osx-64 | linux-aarch64 | osx-arm64 | Version |
example:
| ros-humble-acado-vendor | :x: { data-sort='0' } | :x: { data-sort='0' } | :x: { data-sort='0' } | :x: { data-sort='0' } | :x: { data-sort='0' } |   |
"""

# find all packages that have "data-sort='1'" in the linux-64 column
# this means that the package is supported on linux-64
supported_linux = avail[avail[' linux-64 '].str.contains("data-sort='1'")]

# turn the supported_linux dataframe into a list and remove blank space either side
supported_linux = supported_linux[' Package '].values.tolist()
supported_linux = [x.strip(' ') for x in supported_linux]

# check the packages in the supported_linux dataframe against the ros2_packages list

# write the supported packages to a copy of vinca_yaml file
# replace between 'packages_selected_from_deps:' and 'patch_dir: patch'
with open(cwd + 'sorted_vinca_linux_64.yaml', 'w') as f:
    # write the first part of the file
    for line in vinca_yaml[:vinca_yaml.index('packages_select_by_deps:')+1]:
        f.write(line + '\n')

    # write the supported packages
    for package in ros2_packages:
        if package in supported_linux:
            # remove `ros-humble-` from the start of each line
            package = package.replace('ros-humble-', '')
            f.write('  - ' + package + '\n')

    # delineate the supported packages from the unsupported packages
    f.write('\n  # ---unsupported packages below---\n\n')

    # write the unsupported packages
    for package in ros2_packages:
        if package not in supported_linux:
            # remove `ros-humble-` from the start of each line
            package = package.replace('ros-humble-', '')
            f.write('  # - ' + package + '\n')

    # write the last part of the file
    f.write('\npatch_dir: patch\n')
