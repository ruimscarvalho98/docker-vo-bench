#!/bin/bash
# Apache License 2.0
# Copyright (c) 2017, ROBOTIS CO., LTD.

WORKDIR=/work
echo ""
echo "[Note] Target OS version  >>> Ubuntu 14.04.x (trusty)"
echo "[Note] Target ROS version >>> ROS Indigo Igloo"
echo "[Note] Catkin workspace   >>> $WORKDIR/catkin_ws"
echo ""

echo "[Set the target OS, ROS version and name of catkin workspace]"
name_os_version=${name_os_version:="trusty"}
name_ros_version=${name_ros_version:="indigo"}
name_catkin_workspace=${name_catkin_workspace:="catkin_ws"}

echo "[Update the package lists and upgrade them]"
apt-get update -y
apt-get upgrade -y

echo "[Install build environment, the chrony, ntpdate and set the ntpdate]"
apt-get install -y chrony ntpdate build-essential
ntpdate ntp.ubuntu.com

echo "[Add the ROS repository]"
if [ ! -e /etc/apt/sources.list.d/ros-latest.list ]; then
  sh -c "echo \"deb http://packages.ros.org/ros/ubuntu ${name_os_version} main\" > /etc/apt/sources.list.d/ros-latest.list"
  cat /etc/apt/sources.list.d/ros-latest.list
fi


echo "[Download the ROS keys]"
roskey=`apt-key list | grep "ROS Builder"`
if [ -z "$roskey" ]; then
  apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
fi

echo "[Check the ROS keys]"
roskey=`apt-key list | grep "ROS Builder"`
if [ -n "$roskey" ]; then
  echo "[ROS key exists in the list]"
else
  echo "[Failed to receive the ROS key, aborts the installation]"
  exit 0
fi

echo ""
echo "[Update the package lists and upgrade them]"
apt-get update
apt-get upgrade -y

echo ""
echo "[Install the ros-desktop-full and all rqt plugins]"
apt-get install -y ros-$name_ros_version-desktop-full 
echo ""
echo "[Install all rqt plugins]"
apt-get install -y ros-$name_ros_version-rqt-*

echo ""
echo "[Initialize rosdep]"
sh -c "rosdep init"
rosdep update

echo "[Environment setup and getting rosinstall]"
source /opt/ros/$name_ros_version/setup.sh
apt-get install -y python-rosinstall

sh -c "echo \"source /opt/ros/$name_ros_version/setup.bash\" >> ~/.bashrc"

echo "[Complete!!!]"
exit 0

