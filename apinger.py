import os, time, socket, select, signal, icmp
from heapq import heappush, heappop

def loop(hosts, callback, sleep_interval = 1, timeout_interval = 1):
    sendq = []
    recvq = {}

    jitter = 0
    vario = 0.1
    for host in hosts:
        heappush(sendq, (time.time()+sleep_interval+jitter, host))
        jitter += vario

    psocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    psocket.setblocking(0)
    poller = select.poll()
    poller.register(psocket.fileno(), select.POLLOUT | select.POLLIN)

    my_id = os.getpid()
    seq = 0

    while True:
        events = poller.poll(1)
        current_time = time.time()
        for fileno, event in events:
            if event & select.POLLIN:
                #curent_time = time.time()
                (data, addr) = psocket.recvfrom(2048)
                (r_id, r_seq, time_sent) = icmp.disassemble(data)
                if r_id:
                    rtt = (current_time - time_sent) * 1000
                    #TODO make callback
                    if  r_id == my_id:
                        callback(addr[0], rtt)
                        #print '%16s\t%3s %.3f' % (addr[0], r_seq, rtt)
                        heappush(sendq, (time.time() + sleep_interval, addr[0]))
                        if addr[0] in recvq:
                            del recvq[addr[0]]
            if event & select.POLLOUT:
                if sendq:
                    (time_to_send, ip) = heappop(sendq)
                    if time_to_send < current_time:
                        icmp_packet = icmp.assemble(ip, my_id, seq, current_time)
                        seq += 1
                        psocket.sendto(icmp_packet, (ip,0))
                        recvq[ip] = current_time + timeout_interval
                    else:
                        heappush(sendq, (time_to_send, ip))

        #TODO optimize here
        for ip in [ host for (host, timeout) in recvq.items() if timeout < current_time ]:
            #TODO make callback
            callback(ip, None)
            #print '%16s\ttimeout' % ip
            heappush(sendq, (current_time + sleep_interval, ip))
            del recvq[ip]

        if seq > 10000:
            seq=0




#the end
