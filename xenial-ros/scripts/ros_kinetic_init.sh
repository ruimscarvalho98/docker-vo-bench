#!/bin/bash

echo "[Make the catkin workspace and test the catkin_make]"
echo "[Note] Catkin workspace   >>> $WORKDIR/catkin_ws"
WORKDIR=/work
name_catkin_workspace=${name_catkin_workspace:="catkin_ws"}
name_ros_version=${name_ros_version:="kinetic"}

cd $WORKDIR/$name_catkin_workspace
catkin init
catkin config --merge-devel # Necessary for catkin_tools >= 0.4.
catkin config --extend /opt/ros/$name_ros_version
catkin config --cmake-args -DCMAKE_BUILD_TYPE=Release

cd src
catkin_init_workspace
cd ..
catkin_make

