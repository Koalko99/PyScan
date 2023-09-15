import socket
import aioping
import asyncio

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
a = ".".join(sock.getsockname()[0].split(".")[:-1])
sock.close()
all_ip = (f"{a}.{i}" for i in range(256))

async def check_host(host):
    try:
        await aioping.ping(host)
        return host
    except:
        return
    
async def port_is_open(host, port, timeout=2):
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        writer.close()
        return host, port, socket.getservbyport(port)
    except:
        return False

async def main():
    max_ports = int(input("До какого порта сканировать: "))
    res = list(filter(None, await asyncio.gather(*[asyncio.ensure_future(check_host(ip)) for ip in all_ip])))
    tasks = []
    data = []
    i, j = 500, 0
    for ip in res:
        while i <= max_ports:
            for port in range(j, i):
                tasks.append(asyncio.ensure_future(port_is_open(ip, port)))
            data.extend(list(filter(None, await asyncio.gather(*tasks))))
            i += 500
            j += 500
        i = 500
        j = 0

    data = sorted(list(set(data)))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(3)
        for i in data:
            try:
                sock.connect((i[0], i[1]))
                info = sock.recv(1024).decode().replace("\n", "").replace('\r', "")
                print(f"Host: {i[0]}\nPort: {i[1]}\nService: {i[2]}\nInfo: {info}")
                sock.shutdown(socket.SHUT_RDWR)
            except:
                print(f"Host: {i[0]}\nPort: {i[1]}\nService: {i[2]}")
            if data[-1] != i:
                print("*"*40)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
