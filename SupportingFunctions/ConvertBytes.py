import math

def ConvertBytes(bytes):
    if(bytes == 0):
       return "0B"
    else:
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(bytes, 1024)))
        p = math.pow(1024, i)
        s = round(bytes / p, 2)
        return "%s %s" % (s, size_name[i])

var = ConvertBytes(100000)

print(var)