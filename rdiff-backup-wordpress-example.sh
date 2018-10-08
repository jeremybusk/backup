#!/usr/bin/env bash
#timestamp=$(date "+%Y%m%d%M%H%S")
username="root"
hostname="<your host>"
ipaddr="<your ip address>"
app_dir="/backup/"
src_dirs="/var/www/html /etc"
artifact_dir="${app_dir}/artifacts"
current_dir="${app_dir}/current"
time_series_dir="${app_dir}/time_series_backups/"

if [ ! -d "${current_dir}" ]; then
    mkdir ${current_dir}
fi
if [ ! -d "${artifact_dir}" ]; then
    mkdir ${artifact_dir}
fi
if [ ! -d "${time_series_dir}" ]; then
    mkdir ${time_series_dir}
fi

if [ ! -d "${current_dir}/${hostname}" ]; then
    mkdir -p ${current_dir}/${hostname}
fi

for src_dir in ${src_dirs}; do
echo $src_dir

rsync -avz --relative --delete -e "ssh -i /backup/.ssh/id_rsa -p 22 -C -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress ${username}@${ipaddr}:${src_dir} ${current_dir}/${hostname}/
done
rdiff-backup ${current_dir} ${time_series_dir}

if [ ! -d "${artifact_dir}/${hostname}" ]; then
    mkdir -p ${artifact_dir}/${hostname}
fi
timestamp=$(date "+%Y%m%d%M%H%S")
echo $timestamp
ssh -C -p 22 -l root forum.rchain.coop "mysqldump wordpress | gzip -3 -c" > ${artifact_dir}/${hostname}/wordpress.sql.${timestamp}.gz   
ssh -C -p 22 -l root forum.rchain.coop "mysqldump --all-databases | gzip -3 -c" > ${artifact_dir}/${hostname}/all.sql.${timestamp}.gz   
