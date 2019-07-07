import time
import json
from dnslib import RR, A
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer


class DNSProxyResolver(ProxyResolver):
    """
        DNSProxyResolver - checks if a link is in a blacklist/
        If in: return reply with default answer.
        If not in: passes all requests to upstream DNS server and returns response
    """

    def __init__(self, address, port, host, blacklist, response, timeout=0):
        """
            Parameters
            ----------
            address : str
                The IP address of upper DNS
            port : int
                The port number
            host : str
                The IP address of proxy DNS
            blacklist : list
                The list of strings of names of websites to block
            response : str
                The string that will be used as answer for blocked websites
            timeout : int, optional
                The socket timeout
        """
        ProxyResolver.__init__(self, address, port, timeout)
        self.host = host
        self.blacklist = blacklist
        self.response = response

    def resolve(self, request, handler):
        """
            Provides 'resolve' method which is called by DNSHandler 
            with the decode request (DNSRecord instance) and returns 
            a DNSRecord instance as reply. 
        """
        if request.q.qname in self.blacklist:
            answer = RR(self.response, rdata=A(self.host))
            reply = request.reply()
            reply.add_answer(answer)
            return reply
        return ProxyResolver.resolve(self, request, handler)


if __name__ == "__main__":

    # load config data
    with open("conf.json", "r") as conf_file:
        conf = json.load(conf_file)

    # proxy resolver: resolves an individual host name to an IP address
    resolver = DNSProxyResolver(address=conf["upper_dns"], port=conf["port"], host=conf["host"],
                                blacklist=conf["blacklist"], response=conf["answer"], timeout=conf["socket_timeout"])

    # create and run server
    server = DNSServer(resolver, address=conf["host"], port=conf["port"])

    server.start_thread()

    try:
        while server.isAlive():
            time.sleep(1)
    except KeyboardInterrupt:
        exit()

