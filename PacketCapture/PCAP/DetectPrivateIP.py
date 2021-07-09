import ipaddress

def DetectPrivateIP(subject_address):
    #
    is_private = False
    #
    private_ranges = ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16']
    #
    for addr_range in private_ranges:
        #
        private_range_segments = addr_range.split('.')
        #
        subject_addr_segments  = subject_address.split('.')
        #
        for segment in range(0,len(private_range_segments)):
            #
            if(private_range_segments[segment] == subject_addr_segments[segment]):
                #
                private_hosts = list(ipaddress.ip_network(addr_range))
                #
                if(ipaddress.IPv4Address(subject_address) in private_hosts):
                    #
                    is_private = True
                    #
    return is_private



result = DetectPrivateIP('192.168.1.1') ; print("[*]PrivateIP: ",result)