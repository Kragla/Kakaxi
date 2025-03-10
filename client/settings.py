"""
Settings for Client Tools project.

Generated by 'sosososolong'
"""

import os
import json
import re


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Encoding
ENCODING = 'utf-8'

# Projects
PROJECTS = {
    # Configure a project
    # Choose a name and that name will display as an option in the console for selection
    'my project': {
        # An alias representing this project that may be used in other shell scripts for remote invocation
        # The alias can be passed into the command of remote invocation scripts in the form of a template '{{alias}}'.
        'appalias': 'mpn',
        'project_root': 'D:/myapp.api/',
        'project_file': 'D:/myapp.api/myapp.api.csproj',
        'version_controller': 'D:/myapp.api/VersionController.cs',
        # The directory where the deployment files are located. The supported operations for this directory include
        # uploading updates to a specific directory on the server, packaging it into a zip file and uploading it to a server directory, and executing remote commands
        # based on the UPLOAD configuration
        'path': 'D:/myapp.api/bin/Release/net5.0/publish/',
        # Only file paths containing 'my' and 'Dockerfile' will be uploaded
        'file_include_strs': 'my,Dockfile',
        # Files with paths containing 'appsettings.json' and 'wwwroot' will not be uploaded.
        'file_exclude_strs': 'appsettings.json,wwwroot',
        # Specify the name of the upload directory on the remote server
        'remote_app_dir_name': 'my project'
    }
}


# 私钥路径或者服务器密码
PRIVATEKEY = "C:/Users/YouName/.ssh/id_rsa"


# Upload
UPLOAD = {
    'variables': [
        { 'name': 'remark', 'ignore_source_when_empty': True },
        { 'name': 'commit message', 'ignore_source_when_empty': False }
    ],
    "before_cmds": [
        "dotnet publish -c Release -o {{path}}",
        "git -C {{project_root}} add .",
        "git -C {{project_root}} commit -m'{{commit message}}'"
    ],
    'hosts': (
        # Parameter 1: Server IP;
        # Parameter 2: Port;
        # Parameter 3: Whether to upload a compressed package or a directory for the upload directory;
        # Parameter 4: The location on the server where the 'directory' is being uploaded. The directory name defaults to the project name "my project," or you can explicitly specify it using the property "remote_app_dir_name".
        
        # Parameter 5: remote cmds after upload
        #   {{app_name}} will be replaced with 'my project.zip', and {{appalias}} will be replaced with 'mpn'.
        # Parameter 6: remote cmds before upload
        ("192.168.1.229", 9898, "zip", "/var/wwwroot", ["mv -f /var/wwwroot/{{app_name}} /var/packages/"]),
        ("192.168.1.229", 9898, "dir", "/var/wwwroot", ["publish_images {{appalias}}"]),
    ),
    "after_cmds": [
        "git -C {{project_root}} push",
    ]
}

# kakaxi模板文件位置
KAKAXISETTINGS = {
    'commandPaths': [ "D:/others.projects/tools/resources/CommandSettings" ]
}

# 端口转发
PORT_FORWARD = {
    'jumpServer': {
            "host": "192.168.1.10",
            "port": 22,
            "username": "root",
            "password": "123456"
        },
    'rules': [
        '127.0.0.1:11111 -> 192.168.1.229:11111',
        '127.0.0.1:11112 -> 192.168.1.229:11112',
        '127.0.0.1:11113 -> 192.168.1.229:11113'
    ]
}

# dirname(BASE_DIR) 获取BASE_DIR的父级目录
if os.path.exists(os.path.join(os.path.dirname(BASE_DIR), 'tools_settings.json')):
    settings_file = os.path.join(os.path.dirname(BASE_DIR), 'tools_settings.json')
    data = None
    with open(settings_file, 'r', encoding=ENCODING) as file:
        data = json.loads(file.read())
    if data:
        if 'projects' in data:
            PROJECTS = data["projects"]
        if 'upload' in data:
            UPLOAD = data['upload']
        if 'privatekey' in data:
            PRIVATEKEY = data['privatekey']
        if 'kakaxi' in data:
            KAKAXISETTINGS = data['kakaxi']
        if 'portforward' in data:
            PORT_FORWARD = data['portforward']


if __name__ == '__main__':
    # 作为配置文件, 它不是启动项目, 所以这里的代码不会运行, 可以在这里单独写一些测试程序
    file = "D:\.NET\my\myapp\myapp.api\Controllers\VersionController.cs"
    with open(file, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r'([ \t]+"(\[[^"]*)",)', content, re.S)
        if matches:
            # matches最后一项
            last = print(matches[-1])
