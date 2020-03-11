# ctfd-acm-challenges

用于评测编程题

## Deployment

simply clone this repo into plugins directory:

```
cd <ctfd-dir>/CTFd/plugins
git clone https://github.com/mssctf-dev/ctfd-acm-challenges
```

this plugin requires docker access and /tmp access, so:

```yml
# in docker-compose.yml:
services:
    ctfd:
        ...
        volumes:
            ...
            - /var/run/docker.sock:/var/run/docker.sock
            - /tmp:/tmp
```

run `docker pull mssctf/runner_c_cpp` before first launch  
to support more languages, see `mssctf/runner_*`
