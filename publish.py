from datetime import datetime
import os
import re
from client.file_utils import Uploader, get_path_separator
from client.settings import PROJECTS, ENCODING, UPLOAD, PRIVATEKEY
from client.ssh_conn import SSHConnection


def main():
    # args = sys.argv
    # if len(args) == 1:
    #     return
    
    # target_dir = args[1]

    key_index_dic = {}
    key_index = 1
    for key in PROJECTS.keys():
        key_index_dic.setdefault(str(key_index), key)
        print(f'[{key_index}] {key}')
        key_index += 1
    selected_index = input('请选择要打包的项目:')
    
    # myapp.api
    app_name = key_index_dic[selected_index]
    
    # 要上传的目录D:/xxx/bin/Release/net5.0/publish/(上传方式可能是zip可能是dir)
    uploaded_dir = PROJECTS[app_name]['path'].replace('\\', '/')
    appalias =  PROJECTS[app_name]['appalias']
    project_root = PROJECTS[app_name]['project_root']
    project_file = PROJECTS[app_name]['project_file']
    version_controller = PROJECTS[app_name]['version_controller']
    remote_app_dir_name = PROJECTS[app_name].get('remote_app_dir_name')
    uploading_hosts = PROJECTS[app_name].get('uploading_hosts')

    # 文件需要包含的字符串
    file_include_strs = PROJECTS[app_name]['file_include_strs']
    file_include_strs = None if not file_include_strs else file_include_strs
    file_exclude_strs = PROJECTS[app_name]['file_exclude_strs']
    file_exclude_strs = None if not file_exclude_strs else file_exclude_strs
    
    print(f'uploaded directory: {uploaded_dir}')
    separator = '/'
    
    data_context = {
        'version_controller': { 'value': version_controller, 'ignore_source_when_empty': True },
        'project_root': { 'value': project_root, 'ignore_source_when_empty': False },
        'project_file': { 'value': project_file, 'ignore_source_when_empty': False },
        'path': { 'value': uploaded_dir, 'ignore_source_when_empty': False },
        'appalias': { 'value': appalias, 'ignore_source_when_empty': False },
        'app_name': { 'value': app_name, 'ignore_source_when_empty': False },
        'datetime': { 'value': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'ignore_source_when_empty': False },
        'datetime_short': { 'value': datetime.now().strftime("%y%m%d%H%M"), 'ignore_source_when_empty': False },
    }
    variables = UPLOAD['variables']
    fill_datacontext_by_user_input(variables, data_context, version_controller)

    executingListFlowGroups = {
        "before_cmds": UPLOAD["before_cmds"],
        "after_cmds": UPLOAD["after_cmds"]
    }
    resultListFlowCmdTxtGroups = resolve_cmd_groups(executingListFlowGroups, data_context, app_name)
    before_cmds = resultListFlowCmdTxtGroups.get('before_cmds')
    if before_cmds:
        execute_local_cmd_txts(before_cmds)

    # 上传至多个服务器
    for h in UPLOAD['hosts']:
        host = h[0]
        if uploading_hosts and host not in uploading_hosts:
            continue
        port = h[1]
        transfer_type = h[2]
        host_save_dir = h[3].replace('\\', '/')
        remote_cmds = None
        if len(h) >= 5:
            remote_cmds = h[4]

        if len(h) >= 6:
            remote_cmds_before_upload = h[5]
            execute_remote_cmds(remote_cmds_before_upload, data_context, host)
        
        # 1. 上传文或者目录
        if host_save_dir and transfer_type and transfer_type == 'dir':
            host_app_dir = app_name if remote_app_dir_name is None else remote_app_dir_name
            host_app_dir = host_app_dir if host_save_dir.endswith('/') else f'/{host_app_dir}'
            app_dir_abspath = f'{host_save_dir}{host_app_dir}' # /home/administrator/web/pro_dir
            
            file_include_strs_arr = file_include_strs.split(',') if file_include_strs else None
            file_exclude_strs_arr = file_exclude_strs.split(',') if file_exclude_strs else None
            Uploader(host, port, ENCODING, app_dir_abspath, file_include_strs_arr, file_exclude_strs_arr).upload(uploaded_dir)
        elif transfer_type == 'zip':
            # 截取字符串: strname[start : end : step] 不包含end
            # dir_parts = target_dir[0:bin_index].split(separator)
            
            current_abspath = os.path.abspath('.')
            zips_dir = f'{current_abspath}{separator}zips{separator}'
            if not os.path.exists(zips_dir):
                os.mkdir(zips_dir)
            ziped_file = f'{zips_dir}{app_name}.zip'
            # if os.path.exists(ziped_file) and time() - os.path.getmtime(ziped_file) < 10:
            #     print(f'文件刚刚{datetime.fromtimestamp(os.path.getmtime(ziped_file))}已更新')
            #     return

            if not uploaded_dir.endswith('/') and not uploaded_dir.endswith('\\'):
                uploaded_dir += separator

            cmd = f'7z a .{separator}zips{separator}{app_name}.zip "{uploaded_dir}"'
            print(f'cmd: {cmd}')
            print('开始打包')
            # 正确执行完成返回-1, 失败返回1
            if os.system(cmd) == 1:
                print('打包失败')
                return
            
            # popen的方式需要读取出内容, 单纯的popen()方法不阻塞, cmd命令还没执行完就会执行其他下一行代码
            # with os.popen(cmd, 'r') as zip_log:
            #     zip_log_content = zip_log.read()
            #     print(zip_log_content)
            Uploader(host, port, ENCODING, host_save_dir).upload(ziped_file)
        else:
            print(f'{host}:{port} 未指定zip或者dir的方式上传, 无需连接上传服务器上传目录')
        
        execute_remote_cmds(remote_cmds, data_context, host)

    after_cmds = resultListFlowCmdTxtGroups.get('after_cmds')
    if after_cmds:
        execute_local_cmd_txts(after_cmds)
    print('\n\n\n\n')


# 用户指定变量值
def fill_datacontext_by_user_input(variables, data_context, version_controller):
    for item in variables:
        current = input(f'请输入{item["name"]}:')
        if version_controller and not current and item["name"] == 'version name':
            with open(version_controller, 'r', encoding=ENCODING) as file:
                content = file.read()
                matches = re.compile(r'dev\.v\d+\.\d+\.\d+').findall(content)
                if matches:
                    current = matches[-1]
                    print(f'自动获取版本号: {current}')

        data_context[item["name"]] = {
            'value': current,
            'ignore_source_when_empty': item['ignore_source_when_empty']
        }


def execute_remote_cmds(cmds, data_context, host):
    # ssh连接服务器执行命令
    remote_cmd_executing = ''

    if cmds is not None:
        for cmd_tmpl in cmds:
            cmd = resolve_tmpl(cmd_tmpl, data_context)
            if cmd:
                if cmd.startswith('upload '):
                    print(f'execute: {cmd}')
                    ssh = SSHConnection(host, 22, 'root', PRIVATEKEY)
                    # upload local file to remote server
                    pattern = r'^upload\s+"{0,1}([^"]+)"{0,1}\s+"{0,1}([^"]+)"{0,1}$'
                    match = re.match(pattern, cmd)
                    if match:
                        local_path = match.group(1)
                        remote_path = match.group(2)
                        print(f'upload: {local_path} -> {remote_path}')
                        ssh.upload(local_path, remote_path)
                else:
                    remote_cmd_executing += f'{cmd};'

    if remote_cmd_executing:
        ssh = SSHConnection(host, 22, 'root', PRIVATEKEY)

        print(f'execute: {remote_cmd_executing}')
        stdout, stderr = ssh.exec(remote_cmd_executing)
        print(f'{stdout}\n{stderr}')


def execute_local_cmd_txts(cmd_txts):
    for cmd_txt in cmd_txts:
        print(f'execute cmd local: {cmd_txt}')
        if os.system(cmd_txt) == 1:
            raise Exception(f'命令执行失败: {cmd_txt}')


def resolve_cmd_groups(list_flow_groups, data_context, app_name):
    # 执行本地命令
    not_need_execute_group = []
    executing_list_flow_groups = {}
    for key in list_flow_groups.keys():
        cmds = list_flow_groups[key]
        if cmds is not None:
            for cmd in cmds:
                if type(cmd) == str:
                    cmd = resolve_tmpl(cmd, data_context)
                    if cmd:
                        executing_list_flow_group = executing_list_flow_groups.get(key)
                    if not executing_list_flow_group:
                        executing_list_flow_groups[key] = []
                    executing_list_flow_groups[key].append({'cmdTxt': cmd})
                else:
                    cmdTxt = cmd.get("cmdTxt")
                    cmdProject = cmd.get("project")
                    if cmdProject and app_name not in cmdProject:
                        print(f'项目{app_name}不在{cmdProject}中, 不执行')
                        continue
                    completeFlowGroup = cmd.get("completeFlowGroup")
                    
                    if completeFlowGroup and completeFlowGroup in not_need_execute_group:
                        continue
                    
                    cmdTxt = resolve_tmpl(cmdTxt, data_context)
                    if not cmdTxt:
                        if completeFlowGroup:
                            # 一旦completeFlowGroup中有一个命令无法执行, 当前completeFlowGroup都不需要执行了
                            not_need_execute_group.append(completeFlowGroup)
                        continue
                    
                    cmd['cmdTxt'] = cmdTxt
                    executing_list_flow_group = executing_list_flow_groups.get(key)
                    if not executing_list_flow_group:
                        executing_list_flow_groups[key] = []
                    executing_list_flow_groups[key].append(cmd)
        
        list_flow_cmd_txt_groups = {}
        for key in executing_list_flow_groups.keys():
            executing_list_flow_group = executing_list_flow_groups[key]
            for executingCmd in executing_list_flow_group:
                executingCmdTxt = executingCmd.get("cmdTxt")
                executingCmdCompleteFlowGroup = executingCmd.get("completeFlowGroup")
                if executingCmdCompleteFlowGroup and executingCmdCompleteFlowGroup in not_need_execute_group:
                    continue

                list_flow_cmd_txt_group = list_flow_cmd_txt_groups.get(key)
                if not list_flow_cmd_txt_group:
                    list_flow_cmd_txt_groups[key] = []
                list_flow_cmd_txt_groups[key].append(executingCmdTxt)
        
        return list_flow_cmd_txt_groups

# 解析带模板的字符串
def resolve_tmpl(source, data_context):
    for key in data_context.keys():
        value = data_context[key]["value"]
        if key in source:
            if not value and data_context[key]["ignore_source_when_empty"]:
                return ''
            else:
                source = source.replace('{{'+ key +'}}', value)

    return source


if __name__ == '__main__':
    main()
