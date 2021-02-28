from time import sleep
import socket


def wait_for_tcp(host: str, port: str, timeout=1, wait=1) -> None:
    while True:
        try:
            connection = socket.create_connection(
                (host, port), timeout=timeout)
            connection.close()
            return None
        except:
            sleep(wait)


"""
In shell:

timeout 1 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT"
"""
