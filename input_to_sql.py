import datetime

import MySQLdb as mdb
import re

con = mdb.connect('triste.cefeizz4kcvz.us-west-2.rds.amazonaws.com', 'bendavidkathy', 'bendavidkathy', 'Triste');

cur = con.cursor(mdb.cursors.DictCursor)
#datetime is object, datetime is attribute

def messages_to_sql(message_dict):
    for key,value in message_dict.items():
        b = key
        for item in value:
            c = item[0]
            d = item[1]
            c = c.replace("'","");
            insert = "INSERT INTO UserOneMessages(StringBlock, AlchemyScore, TimeStamp) VALUES ('%s', '%s', '%s');" %(str(c), str(d), str(b))
            cur.execute(insert)
            con.commit()
    

 