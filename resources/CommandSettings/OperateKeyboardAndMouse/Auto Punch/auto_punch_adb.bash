#!/bin/bash

# 定位到当前目录
cd /d/others.projects/

# 生成随机等待时间（60秒到300秒之间）
random_wait=$((RANDOM % 241 + 60))
#sleep $random_wait
# 获取当前时间
current_time=$(date +"%Y-%m-%d %H:%M:%S")
echo ${current_time} 已经等待了${random_wait}秒, 开始打卡

# 检查是否安装了 adb
if ! command -v adb &> /dev/null
then
    echo "未找到 adb 命令。请确保已安装 Android 调试桥 (adb)。"
    exit 1
fi

# 获取设备列表
device_list=$(adb devices | awk 'NR>1 {print $1}')

# 检查设备数量
device_count=$(echo "$device_list" | wc -l)
echo "找到设备数量: $device_count"
# 检查是否有设备连接到计算机
if [[ $device_count -eq 0 ]]; then
    echo "未找到连接的设备。请确保至少有一个设备连接到计算机。"
    /d/.NET/iduo/routine/shell/sendmsg "$(date +"%Y-%m-%d %H:%M:%S") 未找到连接的设备"
    exit 1
fi

# 默认选择第一个设备
device=$(echo "$device_list" | head -n 1)
echo "第一个设备: $device"

# 按下电源键点亮手机屏幕
adb -s $device shell input keyevent KEYCODE_POWER
echo "点亮屏幕"

# 上滑解锁
adb -s $device shell input swipe 780 1888 780 800

# 锁屏密码
adb -s $device shell input tap 539 1892
adb -s $device shell input tap 539 1892
adb -s $device shell input tap 539 1892
adb -s $device shell input tap 539 1892
adb -s $device shell input tap 539 1892
adb -s $device shell input tap 539 1892
echo "已经解锁"

# 打开钉钉
adb -s $device shell am start -n com.alibaba.android.rimet/com.alibaba.android.rimet.biz.LaunchHomeActivity
echo "打开钉钉"

# 等待自动打卡10秒钟
sleep 10
echo "已经等待10秒钟, 打卡完成"

# 回到主界面
adb -s $device shell input keyevent KEYCODE_HOME
echo "回到主界面"

# 按下电源键关闭手机屏幕
adb -s $device shell input keyevent KEYCODE_POWER
echo "按下电源按钮关闭屏幕"
echo ""