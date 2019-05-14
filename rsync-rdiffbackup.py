#!/usr/bin/env python3
# adduser {username} --gecos "" --disabled-password
# mkdir /home/{username}/.ssh
# echo {ssh_public_Key} >> /home/{username}/.ssh/authorized_keys
# chown {username}:{username} -R /home/{username}/.ssh

# rdiff-backup --list-increments rdiff

import subprocess

config = 'bkp.conf'
server_host = 'bkp.host'
server_user = 'example.user' 
server_ssh_port = '22' 
server_public_key = '' 
includes_file = 'includes.dat'
excludes_file = 'excludes.dat'
items_file = 'bkp-items.dat'
client_ssh_key = '/home/example.user/.ssh/id_ed25519'
# delete = ''
delete = '--delete'  # uncomment to allow delete (be careful)
def main():

    client_bkp_items = get_bkp_items(includes_file)
    client_include_items = get_include_items(includes_file)
    client_exclude_items = get_exclude_items(excludes_file)
    # print(client_include_items)
    # print(client_exclude_items)
    # print(client_bkp_items)
    rsync_cmd = build_rsync_cmd(server_host, server_user, client_include_items, client_exclude_items, client_bkp_items)
    print(rsync_cmd)
    run_cmd(rsync_cmd)
    run_rdiff_backup_on_server(server_host, server_user, server_ssh_port)


def  get_bkp_items(bkp_items_file):
    with open(bkp_items_file, 'r') as f:
        bkp_items = f.read().splitlines()
    return bkp_items


def  get_include_items(include_items):
    with open(include_items, 'r') as f:
        include_items = f.read().splitlines()
    return include_items


def  get_exclude_items(exclude_items):
    with open(exclude_items, 'r') as f:
        exclude_items = f.read().splitlines()
    return exclude_items


def run_cmd(cmd):
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        print(r)
        raise Exception(r)


def run_rdiff_backup_on_server(server_host, server_user, server_ssh_port):
    cmd = f'ssh -p {server_ssh_port}  {server_user}@{server_host} "rdiff-backup rsync rdiff"'
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        print(r)
        raise Exception(r)


def build_rsync_cmd(server_host, server_user, client_include_items, client_exclude_items, client_bkp_items):
    includes = ''
    excludes = ''
    # items = f'{server_host}'
    items = ''
    for client_bkp_item in client_bkp_items:
        # items = items + f':{client_bkp_item} '
        items = items + f'{client_bkp_item} '
    for client_include_item in client_include_items:
        includes = includes + f' --include={client_include_item}'
    for client_exclude_item in client_exclude_items:
        excludes = excludes + f' --exclude={client_exclude_item}'
    # Command below uses read from file via python function in this file.
    # rsync_cmd = f'rsync -avz --relative {delete} -e "ssh -p {server_ssh_port} -i {client_ssh_key}" --progress {items} {server_user}@{server_host}:/home/{server_user}/rsync {includes} {excludes}'

    # Command below uses from files.
    # rsync_cmd = f'rsync -avzSuc --recursive --relative {delete} -e "ssh -p {server_ssh_port} -i {client_ssh_key}" --progress --files-from={items_file} / {server_user}@{server_host}:/home/{server_user}/rsync --include-from={includes_file} --exclude-from={excludes_file}'
    rsync_cmd = f'rsync -avSuc --recursive --relative {delete} -e "ssh -p {server_ssh_port} -i {client_ssh_key}" --progress --files-from={items_file} / {server_user}@{server_host}:/home/{server_user}/rsync --include-from={includes_file} --exclude-from={excludes_file}'
    return rsync_cmd


if __name__ == '__main__':
    main()


# Notes
# --include-from 'somefile'
# --exclude-from 'somefile'
# --files-from=FILE 
#      --exclude=PATTERN       exclude files matching PATTERN
#      --exclude-from=FILE     read exclude patterns from FILE
#      --include=PATTERN       don't exclude files matching PATTERN
#      --include-from=FILE     read include patterns from FILE
#      --files-from=FILE
