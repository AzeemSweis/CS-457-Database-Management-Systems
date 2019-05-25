"""
Author: Azeem Sweis
Class: CS 457
Project: PA 1
Date: 2/21/2019
"""

import os
from shutil import rmtree

scopeDir = ""
wrkDir = ""

#Function createDB creates the user specified database and error checks as necessary
def createDB(qb):
    #creating database dir if not already created
    try:
        #storing string that comes after 'create database'
        dir = qb.split("CREATE DATABASE ")[1]
        #checking if specified database exist
        if os.path.exists(dir):
            print "!Failed to create database " + dir + " because it already exists."
        else:
            #creating specified database
            os.makedirs(dir)
            print "Database " + dir + " created."
    except IndexError:
            print "!No database name specified"

#Function dropDB deletes the user specified database and error checks
def dropDB(qb):
    #deleting database dir unless it does not exist
    try:
        #storing string that comes after 'drop database'
        dir = qb.split("DROP DATABASE ")[1]
        #ensure specified database exists
        if os.path.exists(dir):
             rmtree(dir)
             print "Database " + dir + " deleted."
        else:
             print "!Failed to delete database " + dir + " because it does not exist."
    except IndexError:
        print "!No database name specified"

#Function createDB creates the user specified table and error checks
def createTB(qb):
    try:
        #check if we are in correct dir
        correctDB()
        #getting string after create table
        subDir = qb.split("CREATE TABLE ")[1]
        #parsing for passed
        subDir = subDir.split(" (")[0].lower()
        psFile = os.path.join(wrkDir, subDir)
        #print [subDir, psFile, wrkDir]

        if not os.path.isfile(psFile):
            #to create table this will use files which act as tables
            with open(psFile, "w") as TB:
                print "Table " + subDir + " created."
                #start of arg
                if "(" in qb:
                    #creating oList to load & send to file
                    oList = []
                    #remove the (
                    data = qb.split("(",1)[1]
                    #remove the )
                    data = data[:-1]
                    #in data replace the , with |
                    data = data.replace(", " , " | ")
                    #writing user specified data in to user created table
                    TB.write(data)
        else:
            raise ValueError("!Failed to create table " + subDir + " because it already exists.")
    except IndexError:
        print "!Failed to remove table because no table name is specified"
    except ValueError as err:
        print err.args[0]

#Function dropTB deletes the user specified table and error checks as necessary
def dropTB(qb):
    try:
        #check if we are in correct dir
        correctDB()
        #getting string after DROP TABLE
        subDir = qb.split("DROP TABLE ")[1]
        #finding table
        userTB = os.path.join(wrkDir, subDir)
        #checking if table is correct
        if os.path.isfile(userTB):
            #removing table
            os.remove(userTB)
            print "Table " + subDir + " deleted."
        else:
            raise ValueError("!Failed to delete table " + subDir + " because it does not exist.")
    except IndexError:
        print "!Failed to remove table because no table name specified"
    except ValueError as err:
        print err.args[0]


#Function alterTB alters the user table specified and error checks as necessary
def alterTB(qb):
    try:
        #check if we are in correct dir
        correctDB()
        #getting string after ALTER TABLE
        userTB= qb.split("ALTER TABLE ")[1]
        userTB = userTB.split(" ")[0]
        myFile = os.path.join(wrkDir, userTB)
        #checking if myFile is file
        if os.path.isfile(myFile):
            #checking for add
            if "ADD" in qb:
                #using a to append to end of file
                with open(myFile, "a") as TB:
                    newStr = qb.split("ADD ")[1]
                    #write new data to table
                    TB.write(", " + newStr)
                    print "Table " + userTB + " modified."
        else:
            raise ValueError("!Failed to alter table " + userTB + " because it does not exist.")
    except IndexError:
        print "!Failed to remoe table because no table name specified"
    except ValueError as err:
        print err.args[0]


#Function selectStar will query the user specified table and error check as necessary
def selectStar(qb):
    try:
        #check if we are in correct dir
        correctDB()
        #stringing user specified table
        findTB = qb.split("FROM ")[1]
        #user table file
        tbFile = os.path.join(wrkDir, findTB)
        #if table file exists
        if os.path.isfile(tbFile):
            #open table file and print out everything
            with open(tbFile,"r+") as TB:
                newOut = TB.read()
                print newOut
        else:
            raise ValueError("!Failed to query table " + findTB + " because it does not exist.")
    except IndexError:
        print "!Failed to remove table because no table name specified"
    except ValueError as err:
        print err.args[0]

#Function useMe will use the user specified database and error checks as necessary
def useMe(qb):
    try:
        global scopeDir
        #placing database in userDB
        scopeDir = qb.split("USE ")[1]
        #as long as database userDB exists we are now using userDB
        if os.path.exists(scopeDir):
            print "Using database " + scopeDir + " ."
        else:
            raise ValueError("!Failed to use database because it does not exist.")
    except IndexError:
        print "!No database name specified"
    except ValueError:
        print err.args[0]

#Function correctDB ensuring the we are in the correct dir
def correctDB():
    if scopeDir is "":
        raise ValueError("!No database selected")
    else:
        global wrkDir
        wrkDir = os.path.join(os.getcwd(), scopeDir)

#Main function running a simple interface for creating user specified databases
def main():
    try:
        #per instructions
        print "\n"
        while True:
            cmd = ""

            #per instructions dont parse lines with --
            while not ";" in cmd and not "--" in cmd:
                cmd += raw_input()

            #parsing command from test file
            cmd = cmd.split(";")[0]
            cmdStr = str(cmd)
            cmdStr = cmdStr.upper()

            #pass lines with --
            if "--" in cmd:
                pass
            #call createDB if CREATE DATABASE is found
            elif "CREATE DATABASE" in cmdStr:
                createDB(cmd)
            #call dropDB if DELETE DATABASE is found
            elif "DROP DATABASE" in cmdStr:
                dropDB(cmd)
            #call createTB if CREATE TABLE is found
            elif "CREATE TABLE" in cmdStr:
                createTB(cmd)
            #call dropTB if DELETE TABLE is found
            elif "DROP TABLE" in cmdStr:
                dropTB(cmd)
            #call alterTB if ALTER TABLE is found
            elif "ALTER TABLE" in cmdStr:
                alterTB(cmd)
            #call selectStar if SELECT * is found
            elif "SELECT *" in cmdStr:
                selectStar(cmd)
            #call useMe if USE is found
            elif "USE" in cmdStr:
                useMe(cmd)
            #exit if .EXIT is found
            elif ".EXIT" in cmdStr:
                print "All done."
                exit()
    except (EOFError, KeyboardInterrupt) as e:
        print "All done.\n"
        exit()

if __name__ == '__main__':
    main()
