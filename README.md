# ctfd-acm-challenges

用于评测编程题
Work In Progress

## Deployment

simply clone into plugins directory:
```
cd <ctfd-dir>/CTFd/plugins
git clone https://github.com/mssctf-dev/ctfd-acm-challenges
```

this plugin requires docker access, so:

```yml
# in docker-compose.yml:
services:
    ctfd:
        ...
        volumes:
            ...
            - /var/run/docker.sock:/var/run/docker.sock
```

run `docker pull mssctf/c_cpp_judger` before first launch  
to support more languages, see `mssctf/*_judger`
