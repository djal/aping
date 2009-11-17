import time, os, socket, select, icmp
from heapq import heappush, heappop

class Pinger:
    def __init__(self):
        self.__sendqueue__ = []
        self.__id__ = os.getuid()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        self.socket.setblocking(0)

    def add(self, hosts):
        vario = 0.05
        now = time.time()
        for host in hosts:
            self.hosts_by_ip[host.ip] = host
            heappush(self.__sendqueue__, (now+host.die_interval+vario, host))
            vario += vario

    def status(self):
        return [ host for host in self.hosts_by_ip ]

    def start_loop(self):
        self.poller = select.poll()
        self.poller.register(self.socket.fileno(), select.POLLOUT | select.POLLIN)

        while True:
            events = self.poller.poll(1)
            for fileno, event in events:
                if event & select.POLLIN:
                    current_time = time.time()
                    (rec_data, addr) = self.socket.recvfrom(2048)
                    (p_id, seq, time_sent) = icmp.disassemble(rec_data)
                    rtt = (current_time - time_sent) * 1000
                    if addr in self.hosts_by_ip:
                        print "%15s: %.4f ms" % (addr, rtt)
                        heappush(self.__sendqueue__, (time.time() + self.hosts_by_ip[addr].alive_interval, 



