import paramiko
import subprocess
import re
import json
import yaml
import pickle

HOST = None
PINGABLE_HOSTS = []
VALID_PORT = None
USERNAME = "test"
PASSWD = "test"
USERNAME_SQL = "root"
PASSWORD_SQL = ""
RESULT = None

def check_pingable_host():
    last_num = [x for x in xrange(101, 109)]
    ip_line = ["192.168.56." + str(x) for x in last_num[::-1]]
    global PINGABLE_HOSTS

    for i in ip_line:
        print "ping {} ip".format(i)
        cmd = "ping -c 1 %s" % i
        result = subprocess.call(cmd, shell=True, stdout=open("/dev/null", "w"), stderr=subprocess.STDOUT)
        if result == 0:
            print "%s is pingable" % i
            PINGABLE_HOSTS.append(i)

    print "PINGABLE_HOSTS: %s" % PINGABLE_HOSTS


def check_port():
    global HOST
    global VALID_PORT
    global USERNAME
    global PASSWD
    global PINGABLE_HOSTS
    for host in PINGABLE_HOSTS:
        ports = [x for x in xrange(20, 29)]
        for port in ports:
            try:
                print "trying host: {}, port: {}".format(host, port)
                t = paramiko.Transport((host, port))
                t.connect(username=USERNAME, password=PASSWD)
                HOST = host
                VALID_PORT = port
                print "host = {}, port = {}".format(host, port)
                return HOST, VALID_PORT
            except paramiko.AuthenticationException:
                print 'Authentication failed'
            except paramiko.SSHException:
                print 'SSHException error'
            except Exception as ex:
                print ex

def searching_for_password_sql():
    global PASSWORD_SQL
    global HOST
    global USERNAME
    global PASSWD
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOST, username=USERNAME, password=PASSWD)

    stdin, stdout, stderr = ssh.exec_command("grep -r 'password=.*/n' /home/test")
    string = stdout.read().splitlines()
    pswd = re.split('password=', string[0])
    pswd = re.split('/n', pswd[1])
    PASSWORD_SQL = pswd[0]
    print "PASSWORD_SQL: %s" % PASSWORD_SQL

def packer():
    global PASSWORD_SQL, HOST, PORT, USERNAME, PASSWD
    js_file = dict(host = HOST, port = PORT)
    json.dump(js_file, open('fedorov-server.json', 'w'))

    ya_file = dict(username = USERNAME_SQL, password = PASSWORD_SQL)
    with open('fedorov-sql.yaml', 'w') as f:
        f.write(yaml.dump(ya_file, default_flow_style=True))

    with open('fedorov-bin_backup.pickle', 'wb') as f:
        pickle.dump([js_file, ya_file], f)

def worker():
    global HOST
    global VALID_PORT
    global USERNAME
    global PASSWD
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=USERNAME, password=PASSWD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    localpath = '/home/alex/PycharmProjects/untitled/worker.py'
    remotepath = '/home/test/worker.py'
    sftp.put(localpath, remotepath)

    sftp.close()
    transport.close()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOST, username=USERNAME, password=PASSWD)
    stdin, stdout, stderr = ssh.exec_command("python /home/test/worker.py {}".format(PASSWORD_SQL))
    RESULT = stdout
    for i in RESULT:
        print i
    return RESULT

if __name__ == "__main__":
    print "check pingable host"
    check_pingable_host()
    print "check port"
    check_port()
    print "searching for password sql"
    searching_for_password_sql()
    print "packer"
    packer()
    print "worker"
    worker()
