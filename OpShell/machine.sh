#!/bin/bash
ip2name(){
    ip="$1"
    name=$(/usr/local/mysql/bin/mysql -N -uroot -phipu_2011 -e "SELECT hostname FROM falcon_portal.host where ip = '$ip';" 2>/dev/null)
    echo ${name}
}
main(){
for group in $(/usr/local/mysql/bin/mysql -N -uworker -pservices -h10.101.1.140 -e 'SELECT srv_name FROM machine_manage_db.srv_machine where machine like "10.%" group by srv_name;' 2>/dev/null )
do
    gname=$(echo $group| sed 's/||/\//g')
    temp_n=""
    for machine in $(/usr/local/mysql/bin/mysql -N -uworker -pservices -h10.101.1.140 -e "SELECT machine FROM machine_manage_db.srv_machine where srv_name = '${group}' and machine like '10.%' group by machine;" 2>/dev/null)
    do
        t_name=$(ip2name "${machine}")
        if [ "x${t_name}" == "x" ]
            then
            continue
        else
            temp_n="${t_name}|${temp_n}"
        fi
    done
        if [ "x${temp_n}" == "x" ]
            then
                continue
            else
                chk=$(/usr/local/mysql/bin/mysql -N -uroot -phipu_2011 -e "SELECT count(name) FROM dashboard.dashboard_screen where name = '${gname}';" 2>/dev/null)
                if [ ${chk} == 0 ]
                    then
                        /usr/local/mysql/bin/mysql -usageskr -pskr1986 -h10.101.2.35 -e "insert into dashboard.dashboard_screen(pid,name) value(38,'${gname}');" 2>/dev/null
                fi
                insert_id=$(/usr/local/mysql/bin/mysql -N -uroot -phipu_2011 -e "SELECT id FROM dashboard.dashboard_screen where name = '${gname}';" 2>/dev/null)
                # echo "${chk} ${insert_id}"
                chk_p=$(/usr/local/mysql/bin/mysql -N -uroot -phipu_2011 -e "SELECT count(screen_id) FROM dashboard.dashboard_graph where screen_id = ${insert_id};" 2>/dev/null)
                if [ ${chk_p} != 3 ]
                    then
                        /usr/local/mysql/bin/mysql -usageskr -pskr1986 -h10.101.2.35 -e "insert into dashboard.dashboard_graph(title, hosts, counters, screen_id) values('base','${temp_n%|}', 'load.1min|load.5min|cpu.user|cpu.system|cpu.idle|mem.memfree.percent|cpu.iowait|ss.estab|ss.timewait',${insert_id}); " 2>/dev/null
                        /usr/local/mysql/bin/mysql -usageskr -pskr1986 -h10.101.2.35 -e "insert into dashboard.dashboard_graph(title, hosts, counters, screen_id, graph_type) values('net','${temp_n%|}','metric=net.if.in.bytes|metric=net.if.out.bytes',${insert_id},'a'); " 2>/dev/null
                        /usr/local/mysql/bin/mysql -usageskr -pskr1986 -h10.101.2.35 -e "insert into dashboard.dashboard_graph(title, hosts, counters, screen_id, graph_type) values('disk','${temp_n%|}','metric=df.bytes.free.percent',${insert_id},'a'); " 2>/dev/null
                else
                    /usr/local/mysql/bin/mysql -usageskr -pskr1986 -h10.101.2.35 -e "update dashboard.dashboard_graph set hosts='${temp_n%|}' where screen_id = ${insert_id};"
                fi
                echo "${temp_n%|}"
        fi
done
}
if [ -e /home/worker/OpShell/cron/machine/lock ]
then
	exit
else
	main
fi 
