import sqlite3
import os

def VTK_makeDB(dbName):
    dbg = False
    try:
        connection = sqlite3.connect(dbName)
    except:
        print "Cannot connect to table"
        exit()
    try:
        connection.execute('''CREATE TABLE ACCOUNTS
       (    ACCOUNTNUMBER   INT PRIMARY KEY     NOT NULL,               
            PIN             INT                 NOT NULL,
            NAME            TEXT                NOT NULL,
            ADDRESS         CHAR(50),
            BALANCE         REAL);''')
    except:
        if dbg: print "Did not create table - it already exists."
    connection.close()
    VTK_insertDataInDB(dbName)


def VTK_insertDataInDB(dbName):
    dbg = False
    conn = sqlite3.connect(dbName)
    try:
        conn.execute("INSERT INTO ACCOUNTS (ACCOUNTNUMBER,PIN,NAME,ADDRESS,BALANCE) \
              VALUES (1111, 1111, 'Phil',  'California', 20000.00 )");
        conn.execute("INSERT INTO ACCOUNTS (ACCOUNTNUMBER,PIN,NAME,ADDRESS,BALANCE) \
              VALUES (2222, 2222, 'Travis',  'Texas', 15000.00 )");
        conn.execute("INSERT INTO ACCOUNTS (ACCOUNTNUMBER,PIN,NAME,ADDRESS,BALANCE) \
              VALUES (3333, 3333, 'Nikko',  'Norway', 20000.00 )");
        conn.execute("INSERT INTO ACCOUNTS (ACCOUNTNUMBER,PIN,NAME,ADDRESS,BALANCE) \
              VALUES (4444, 4444, 'Ming',  'China', 65000.00 )");
        conn.commit()
        if dbg: print "Records created successfully";
    except:
        pass
    conn.close()

def VTK_selectAllDataFromDB(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.execute("SELECT *  from ACCOUNTS")
    for row in cursor:
       print row
    conn.close()

def VTK_updateBalanceDB(dbName,acctNumber,newBalance):
    dbg = False
    conn = sqlite3.connect(dbName)
    sqlStr = "UPDATE ACCOUNTS set BALANCE = " + str(newBalance) + " where ACCOUNTNUMBER=" + str(acctNumber)
    if dbg: print sqlStr
    conn.execute(sqlStr)
    conn.commit()
    if dbg: print "Total number of rows updated :", conn.total_changes
    conn.close()

def VTK_doesAccountNumberAndPINMatch(dbName,acctNumber,PIN):
    dbg = False
    conn = sqlite3.connect(dbName)
    sqlStr = "SELECT *  from ACCOUNTS where ACCOUNTNUMBER=" + str(acctNumber) + " AND PIN=" + str(PIN)
    if dbg: print sqlStr
    cursor = conn.execute(sqlStr)
    if dbg:
        for row in cursor:
            print row
    exist = cursor.fetchone()
    conn.close()
    if exist:
        return 'True'
    else:
        return 'False'

if __name__ == "__main__":
    dbName = 'VTK_DB.db'
    VTK_makeDB(dbName)                                          # make the database and table structure
    #VTK_insertDataInDB(dbName)                                  # populate it with some data
    VTK_updateBalanceDB(dbName,1111,1.0)                        # update the balance on an account
    VTK_selectAllDataFromDB(dbName)                             # print out the database
    VTK_updateBalanceDB(dbName,1111,123.45)                     # update the balance again
    VTK_selectAllDataFromDB(dbName)                             # print out the database
    print VTK_doesAccountNumberAndPINMatch(dbName,1111,1111)    # check if account number and PIN match
    print VTK_doesAccountNumberAndPINMatch(dbName,1111,2222)    # check if account number and PIN match   
   