#!/bin/bash
declare -A pid_to_container
declare -A seen_bind_ports

for cid in $(docker ps -q); do
    for pid in $(docker top "$cid" -eo pid | tail -n +2); do
        pid_to_container[$pid]=$cid
    done
done

netstat -tulnp | awk '$6 == "LISTEN" {split($4, a, ":"); split($7, b, "/"); print a[length(a)], b[1]}' | sort -u | while read -r port pid; do
    found_id="${pid_to_container[$pid]}"
    if [[ -n "$found_id" ]]; then
        name=$(docker inspect --format '{{.Name}}' "$found_id" | sed 's/^\/\+//')
        echo "$name  $port"
    fi
done

docker ps --format '{{.ID}} {{.Names}} {{.Ports}}' | while read -r cid name ports; do
    if [[ -n "$ports" ]]; then
        echo "$ports" | grep -oE '[0-9]+->' | sed 's/->//' | while read -r port; do
            key="$name:$port"
            if [[ -z "${seen_bind_ports[$key]}" ]]; then
                seen_bind_ports[$key]=1
                echo "$name  $port"
            fi
        done
    fi
done
