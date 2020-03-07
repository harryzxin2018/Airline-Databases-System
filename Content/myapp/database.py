import pymysql.cursors

#Configure MySQL
conn = pymysql.connect(host='192.168.64.2',
                       user='zixin',
                       password='password',
                       db='air_ticket_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)