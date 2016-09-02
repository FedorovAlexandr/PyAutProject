import os
import hashlib
import pymysql
import sys

PASSWORD_SQL = sys.argv[1]

def razbor():
    files_found = []
    for target_folder, subdirs, filenames in os.walk('/home/test/dir1'):
        for filename in filenames:
            files_found.append(os.path.join(target_folder, filename))
    print files_found
    return files_found
razbor()

file_dict = {}
local_files = razbor()
for local_file in local_files:
    file_dict[local_file] = hashlib.md5(open(local_file, 'rb').read()).hexdigest()
print file_dict

connection = pymysql.connect(host="localhost",
                             user="root",
                             password=PASSWORD_SQL)

try:
    with connection.cursor() as cur:
        sql = "CREATE DATABASE IF NOT EXISTS FINAL_TEST"
        cur.execute(sql)
        connection.commit()
finally:
    connection.close()

connection = pymysql.connect(host="localhost",
                             user="root",
                             password=PASSWORD_SQL,
                             db="FINAL_TEST",
                             charset="utf8mb4",
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cur:
        sql = """CREATE TABLE IF NOT EXISTS FEDOROV(file varchar(100),
                 hash varchar(35))"""
        cur.execute(sql)
        connection.commit()

        sql = "INSERT INTO FEDOROV(file, hash) VALUES(%s, %s)"
        for k, v in file_dict.items():
            cur.execute(sql, (k.split(os.sep)[-1], v))
            connection.commit()
finally:
    connection.close()
