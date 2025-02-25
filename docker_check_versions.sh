#!/bin/bash

Stopped="--all"
SearchName=""
regbin="regctl"

containers=($(docker ps $Stopped --filter "name=$SearchName" --format '{{.Names}}'))

check_updates() {
  local container=$1
  local repoUrl=$(docker inspect "$container" --format='{{.Config.Image}}')
  local imageId=$(docker inspect "$container" --format='{{.Image}}')
  local localHash=$(docker image inspect "$imageId" --format '{{.RepoDigests}}' 2>/dev/null)
  local regHash=$($regbin image digest --list "$repoUrl" 2>/dev/null)

  if [[ "$localHash" != *"$regHash"* ]]; then
    echo "$container yes"
  else
    echo "$container no"
  fi
}

for container in "${containers[@]}"; do
  check_updates "$container" &
done
wait
