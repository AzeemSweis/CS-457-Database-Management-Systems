'''
Azeem Sweis
CS 457
Project 4 - Built off of Projects 3, 2, and 1
'''

import os, re
from contextlib import contextmanager #needed for multiple file opening

def main():
    globalScpDir = ""
    workingDir = ""
    lockArray = ["table"]
    lockFlag = 0
    lockIndex = 1

    try:
        if not os.path.exists("./locks"):  # Only create it if it doesn't exist
            os.makedirs("./locks")

        while True:
            clInput = ""

            #print lockArray, lockFlag
            if lockFlag is 1:
                if lockIndex is not len(lockArray):
                    clInput = lockArray[lockIndex]
                    lockIndex += 1
                else:
                    toRemove = "./locks/" + lockArray[0]
                    if os.path.isfile(toRemove):
                        os.remove(toRemove)
                    lockArray = ["table"]
                    lockIndex = 1
                    lockFlag = 0

            if lockFlag is not 1:
                while not ";" in clInput and not "--" in clInput:
                    clInput += raw_input("\n enter a command \n").strip('\r')  #Read clInput command from terminal
                clInput = clInput.split(";")[0]  #Remove ; from the clInput command

            inputString = str(clInput)  #Normalize the clInput command
            inputString = inputString.upper()

            #print inputString

            if "--" in clInput:  #Pass the comments
                pass

            elif "ALTER TABLE" in inputString:
                alterTable(clInput)

            elif "BEGIN TRANSACTION" in inputString:
                lockArray, lockFlag = transaction(lockArray, lockFlag)

            elif "CREATE DATABASE" in inputString:
                createDatabase(clInput)

            elif "CREATE TABLE" in inputString:
                createTable(clInput)

            elif "DELETE FROM" in inputString:
                deleteFrom(clInput)

            elif "DROP DATABASE" in inputString:
                dropDatabase(clInput)

            elif "DROP TABLE" in inputString:
                dropTable(clInput)

            elif "INSERT INTO" in inputString:
                insertInto(clInput)

            elif "SELECT" in inputString:
                selectInput(clInput, inputString)

            elif "UPDATE" in inputString:
                updateFrom(clInput)

            elif "USE" in inputString:
                useDatabase(clInput)

            elif ".EXIT" in clInput:  #Exit database if specified before EOF
                print "All done."
                exit()

    except (EOFError, KeyboardInterrupt) as e:  #Exit script elegantly
        print "\n Connection to database terminated."

#Primary Functions

@contextmanager
def MultiFileManager(files, mode='rt'):
    """ Open multiple files and make sure they all get closed. """
    files = [open(file, mode) for file in files]
    yield files
    for file in files:
        file.close()

def useEnabled():  #Catch the error when a database hasn't been enabled
    if globalScpDir is "":
        raise ValueError("!Failed to use table because no database was selected.")
    else:
        global workingDir
        workingDir = os.path.join(os.getcwd(), globalScpDir)

def returnColIndex(data):
    colIndex = data[0].split(" | ")
    for x in range(len(colIndex)):
        colIndex[x] = colIndex[x].split(" ")[0]
    return colIndex

def splitLines(line):
    lineCheck = line.split(" | ")
    for x in range(len(lineCheck)):  #Check that each column has an item
        lineCheck[x] = lineCheck[x].split(" ")[0]
    return lineCheck

def joinWhere(searchItem, tableVariables, dataArray, joinType = 'inner'):
    counter = 0
    out = []
    flag = 0
    num_tables = len(dataArray)
    matched_data = []
    emptyCols = ""

    #Collect column data in array and see if it matches
    if "=" in searchItem:  #Operator evaluation
        if "!=" in searchItem:
            r_col = searchItem.split(" !=")[0]
        else:
            leftSearch = searchItem.split(" =")[0]
            leftSearch = leftSearch.split(".")[1]
            rightSearch = searchItem.split("= ")[1]
            rightSearch = rightSearch.split(".")[1]
    if num_tables == 2:
        leftTable = dataArray[0]
        rightTable = dataArray[1]
    else:
        print "!JOIN ONLY ACCEPTS TWO TABLES."
        return -1, -1

    leftData = []
    rightData = []
    leftColumn = returnColIndex(leftTable[0])
    rightColumn = returnColIndex(rightTable[0])

    for line in leftTable:

        lineSplit = splitLines(line)
        leftData.append(lineSplit[leftColumn.index(leftSearch)])
    for line in rightTable:
        lineSplit = splitLines(line)
        rightData.append(lineSplit[rightColumn.index(rightSearch)])

    #If both the inner and outer joins start with matching data
    for x in range(len(leftData)):
        for y in range(len(rightData)):
            if leftData[x] == rightData[y]:
                rightTable[y] = rightTable[y].strip('\n')
                out.append(rightTable[y] + ' | ' + leftTable[x])
                counter += 1
                if joinType == 'left':
                    matched_data.append(leftTable[x])

    if joinType == 'left':
        numData = len(rightColumn)
        for x in range(numData):
            emptyCols += ' | '
        for x in range(len(leftData)):
            if not leftColumn[0] in leftTable[x]: #Remove the table key
                if not leftTable[x] in matched_data: #Dont run unless there are no matches foor this data
                    out.append(leftTable[x].strip('\n') + emptyCols )
                    counter += 1
    return counter, out

def where(argumentToFind, action, data, up_val=""):
    counter = 0
    colIndex = returnColIndex(data)
    attr_name = colIndex
    inputData = list(data)
    out = []
    flag = 0
    if "=" in argumentToFind:  #Figure out the operator for splitting up the input
        if "!=" in argumentToFind:
            r_col = argumentToFind.split(" !=")[0]
            flag = 1
        else:
            r_col = argumentToFind.split(" =")[0]

            argumentToFind = argumentToFind.split("= ")[1]
        if "\"" in argumentToFind or "\'" in argumentToFind: #Cleanup var
            argumentToFind = argumentToFind[1:-1]
        for line in data:
            line_test = splitLines(line)
            if argumentToFind in line_test:
                colIndex = attr_name.index(r_col)
                line_index = line_test.index(argumentToFind)
                if line_index == colIndex:
                    if action == "delete":
                        del inputData[inputData.index(line)]
                        out = inputData
                        counter += 1
                    if action == "select":
                        out.append(inputData[inputData.index(line)])
                    if action == "update":
                        attribute, field = up_val.split(" = ")
                        print attribute, field
                        if attribute in attr_name:
                            sep_line = splitLines(line)
                            sep_line[attr_name.index(attribute)] = field.strip().strip("'")
                            inputData[inputData.index(line)] = ' | '.join(sep_line)
                            out = inputData
                            counter += 1

    elif ">" in argumentToFind:  # Evaluate operator
        r_col = argumentToFind.split(" >")[0]
        argumentToFind = argumentToFind.split("> ")[1]
        for line in data:
            line_test = line.split(" | ")
            for x in range(len(line_test)):  #Evaluate each column item
                line_test[x] = line_test[x].split(" ")[0]
                try:
                    line_test[x] = float(line_test[x])  #Check value
                    if line_test[x] > float(argumentToFind):
                        temp_col = colIndex.index(r_col)
                        if x == temp_col:  # Check for column
                            if action == "delete":
                                del inputData[inputData.index(line)]  #Remove matching field
                                out = inputData
                                counter += 1
                            if action == "select":
                                out.append(inputData[inputData.index(line)])
                            if action == "update":
                                print "hello!"
                except ValueError:
                    continue
    if flag:
        out = list(set(data) - set(out))
    return counter, out

#Secondary Functions

def alterTable(clInput):
    try:
        useEnabled()  # Check that a database is selected
        tableName = clInput.split("ALTER TABLE ")[1]
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDir, tableName)
        if os.path.isfile(fileName):
            if "ADD" in clInput:  # Only checks for during first project
                with open(fileName, "a") as table:  # Use A to append data to end of the file
                    additionalString = clInput.split("ADD ")[1]
                    table.write(" | " + additionalString)
                    print "Table " + tableName + " modified."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist."
    except IndexError:
        print "!Failed to alter Table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def transaction(lockArray, lockFlag):
    try:
        fileName = ""
        files = []
        useEnabled()  # Check that there is a database is selected

        while True:
            clInput = ""

            while not ";" in clInput and not "--" in clInput:
                clInput += raw_input("\n enter a command \n").strip('\r')  # Read the clInput command from terminal

            if "commit;" in clInput:
                break

            clInput = clInput.split(";")[0]  # Remove ; from the clInput command
            inputString = str(clInput)  # Normalize the clInput command
            lockArray.append(inputString)

            if "UPDATE" in inputString.upper():
                tableName = re.split("UPDATE ", lockArray[1], flags=re.IGNORECASE)[1]  # Get an updated string to use for the table name
                tableName = re.split("SET", tableName, flags=re.IGNORECASE)[0].lower().strip()
                fileName = tableName + ".lock"
                files = os.listdir("./locks")
                lockArray[0] = fileName

                path = "./locks/" + fileName
                f = open(path, "w")
                f.close()
                lockFlag = 1

        if fileName in files:
            print "Error: Table", tableName, "is locked!" # Print Error
            return ["table"], 0
        return lockArray, lockFlag

    except IndexError:
        print "!Something went wrong in 'transaction'."

    except ValueError as err:
        print err.args[0]

def createDatabase(clInput):
    try:
        directory = clInput.split("CREATE DATABASE ")[1]  # Store the string after CREATE DATABASE
        if not os.path.exists(directory):  # Only create it if it doesn't exist
            os.makedirs(directory)
            print "Database " + directory + " created."
        else:
            print "!Failed to create database " + directory + " because it already exists."
    except IndexError:
        print "!Failed to create database because no database name specified."

def createTable(clInput):
    try:
        useEnabled()  # Check that database is enabled and selected
        sub_dir = re.split("CREATE TABLE ", clInput, flags=re.IGNORECASE)[1]  # Get a string to use for the table name
        sub_dir = sub_dir.split("(")[0].lower()
        fileName = os.path.join(workingDir, sub_dir)
        if not os.path.isfile(fileName):
            with open(fileName, "w") as table:  # Create a file within folder to act as a table
                print "Table " + sub_dir + " created."
                if "(" in clInput:  # Check for the start of argument section
                    out = []  # Create a list for output to file
                    data = clInput.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    counter = data.count(",")  # Count num of table arguments
                    for x in range(counter + 1):
                        out.append(data.split(", ")[
                                       x])  # Import args to list for printing
                    table.write(" | ".join(out))  # Output array to the file
        else:
            print "!Failed to create table " + sub_dir + " because it already exists."
    except IndexError:
        print "!Failed to create table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def deleteFrom(clInput):
    try:
        useEnabled()  # Check that a database is selected
        tableName = re.split("DELETE FROM ", clInput, flags=re.IGNORECASE)[1]  # Get a string to use for the table name
        tableName = tableName.split(" ")[0].lower()
        fileName = os.path.join(workingDir, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()
                delete_item = re.split("WHERE ", clInput, flags=re.IGNORECASE)[1]
                counter, out = where(delete_item, "delete", data)
                table.seek(0)
                table.truncate()
                for line in out:
                    table.write(line)
                if counter > 0:
                    print counter, " records deleted."
                else:
                    print "No records deleted."
        else:
            print "!Failed to delete table " + tableName + " because it does not exist."
    except IndexError:
        print "!Failed to delete table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def dropDatabase(clInput):
    try:
        directory = clInput.split("DROP DATABASE ")[1]  # Save string after DROP DATABASE
        if os.path.exists(directory):  # Check db already exists, otherwise can't delete
            for remove_val in os.listdir(directory):  # Empty and remove folder
                os.remove(directory + "/" + remove_val)
            os.rmdir(directory)
            print "Database " + directory + " deleted."
        else:
            print "!Failed to delete database " + directory + " because it does not exist."
    except IndexError:
        print "!No database name specified."

def dropTable(clInput):
    try:
        useEnabled()  # Check that a database is selected
        sub_dir = clInput.split("DROP TABLE ")[1].lower()  # Get string to use for the table name
        path_to_table = os.path.join(workingDir, sub_dir)
        if os.path.isfile(path_to_table):
            os.remove(path_to_table)
            print "Table " + sub_dir + " deleted."
        else:
            print "!Failed to delete Table " + sub_dir + " because it does not exist."
    except IndexError:
        print "!Failed to remove Table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def insertInto(clInput):
    try:
        useEnabled()  # Check database is enabled and selected
        tableName = clInput.split(" ")[2].lower()  # Get table name
        fileName = os.path.join(workingDir, tableName)
        if os.path.isfile(fileName):
            if "values" in clInput:  # Check for start of argument section
                with open(fileName, "a") as table:  # Open the file to insert into
                    out = []  # Create list for output to file
                    data = clInput.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    counter = data.count(",")  # Count argument number
                    for x in range(counter + 1):
                        out.append(data.split(",")[
                                       x].lstrip())  # Import arguments for printing
                        if "\"" == out[x][0] or "\'" == out[x][0]:
                            out[x] = out[x][1:-1]
                    table.write("\n")
                    table.write(" | ".join(out))  # Output the array to a file
                    print "1 new record inserted."
            else:
                print "!Failed to insert into " + tableName + " because there were no specified arguments."
        else:
            print "!Failed to alter table " + tableName + " because it does not exist."
    except IndexError:
        print "!Failed to insert into table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def selectInput(input, inputUp):
    try:
        useEnabled()  #Check that a database is selected
        tableName = re.split("FROM ", input, flags=re.IGNORECASE)[1].lower()  #Get string to use for the table name
        if "WHERE" in inputUp:
            tableName = re.split("WHERE", tableName, flags=re.IGNORECASE)[0]
            if " " in tableName:
                tableName = tableName.split(" ")[0]
        fileName = os.path.join(workingDir, tableName)
        output = ""
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:  #Since there should already be tables created, use r+
                if "WHERE" in inputUp: #Using the where to find the matches with all attributes
                    itemToFind = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                    data = table.readlines()
                    mainCount, output = where(itemToFind,"select",data)
                    for line in output:
                        print line
                if "SELECT *" in inputUp:
                    if not output == "": #Checks if the output is allocated
                        for line in output:
                            print line
                    else:
                        output = table.read()
                        print output
                else: #If doesnt want all attributes, trim down output
                    arguments = re.split("SELECT", input, flags=re.IGNORECASE)[1]
                    attributes = re.split("FROM", arguments, flags=re.IGNORECASE)[0]
                    attributes = attributes.split(",")
                    if not output == "":  #This checks if the output is allocated
                        lines = output
                    else:
                        lines = table.readlines()
                        data = lines
                    for line in lines:
                        out = []
                        for attribute in attributes:
                            attribute = attribute.strip()
                            colIndex = returnColIndex(data)
                            if attribute in colIndex:
                                splitLine = splitLines(line)
                                out.append(splitLine[colIndex.index(attribute)].strip())
                        print " | ".join(out)
        else:
            print "!Failed to query table " + tableName + " because it does not exist."
    except IndexError:
        print "!Failed to select because no table name is specified."
    except ValueError as err:
        print err.args[0]

def joinOn(clInput,inputUp):
    toJoinOn = re.split("on", clInput, flags=re.IGNORECASE)[1]

    if "INNER" in inputUp:
        return joinWhere(searchItem, tableVariables, dataArray)

    if "OUTTER" in inputUp:
        if "LEFT" in inputUp:
            counter, out = where(toJoinOn, "SELECT", data)
            for line in data:
                for matchedData in out:
                    print "hi"
        elif "RIGHT" in inputUp:
            counter, out = where(toJoinOn, "SELECT", data)

def updateFrom(clInput):
    try:
        useEnabled()  #Check that a database is selected
        tableName = re.split("UPDATE ", clInput, flags=re.IGNORECASE)[1]
        tableName = re.split("SET", tableName, flags=re.IGNORECASE)[0].lower().strip()
        fileName = os.path.join(workingDir, tableName)
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:
                data = table.readlines()
                update_item = re.split("WHERE ", clInput, flags=re.IGNORECASE)[1]
                val = re.split("SET ", clInput, flags=re.IGNORECASE)[1]
                val = re.split("WHERE ", val, flags=re.IGNORECASE)[0]
                counter, out = where(update_item, "update", data, val)
                table.seek(0)
                table.truncate()
                for line in out:
                    if not "\n" in line:
                        line += "\n"
                    table.write(line)
                if counter > 0:
                    print counter, " records modified."
                else:
                    print "No records modified."
        else:
            print "!Failed to update table " + tableName + " because it does not exist."
    except IndexError:
        print "!Failed to update table because no table name is specified."
    except ValueError as err:
        print err.args[0]

def useDatabase(clInput):
    try:
        global globalScpDir
        globalScpDir = clInput.split("USE ")[1]  # Store the string after USE (with global scope)
        if os.path.exists(globalScpDir):
            print "Using database " + globalScpDir + " ."
        else:
            raise ValueError("!Failed to use database because it does not exist.")
    except IndexError:
        print "!No database name specified"
    except ValueError as err:
        print err.args[0]

def selectHelper(fileNames, tableVariables, joinType, inputUp, clInput):
    tableArray = []
    table_lookup = {}
    tableNames = []

#TableName Parsing
    if "JOIN" in inputUp:
        trimmed_input = re.split("FROM ", clInput, flags =re.IGNORECASE)[1]
        #The left table will always be [0]

        if "LEFT" in inputUp:
            leftTableName = re.split("LEFT", trimmed_input, flags=re.IGNORECASE)[0].lower()
            rightTableName = re.split("JOIN ", trimmed_input, flags=re.IGNORECASE)[1].lower()
            rightTableName = re.split("ON", rightTableName, flags=re.IGNORECASE)[0].strip()
            leftTableName = re.split(" ", leftTableName, flags=re.IGNORECASE)[0].strip()
            rightTableName = re.split(" ", rightTableName, flags=re.IGNORECASE)[0].strip()
            tableArray.append(leftTableName) #left table
            tableArray.append(rightTableName) #right table
            joinType = 'left'

        elif "INNER" in inputUp:
            leftTableName = re.split("INNER", trimmed_input, flags=re.IGNORECASE)[0].lower()
            rightTableName = re.split("JOIN ", trimmed_input, flags=re.IGNORECASE)[1].lower()
            rightTableName = re.split("ON", rightTableName, flags=re.IGNORECASE)[0].strip()
            leftTableName = re.split(" ", leftTableName, flags=re.IGNORECASE)[0].strip()
            rightTableName = re.split(" ", rightTableName, flags=re.IGNORECASE)[0].strip()
            tableArray.append(leftTableName) #left table
            joinType = 'inner'
            tableArray.append(rightTableName) #right table

        elif "RIGHT" in inputUp: #Not currently implemented
            tableArray = re.split("RIGHT", trimmed_input, flags=re.IGNORECASE)[0].lower() #left table
            tableArray = re.split("JOIN", trimmed_input, flags=re.IGNORECASE)[1].lower() #right table
            joinType = 'right'

    elif "WHERE" in inputUp:
        tableNames = re.split("FROM ", clInput, flags=re.IGNORECASE)[1].lower()
        tableNames = re.split("WHERE", tableNames, flags=re.IGNORECASE)[0]

    else: #if not join or where
        tableNames = re.split("FROM ", clInput, flags=re.IGNORECASE)[1].lower()
        if "," in tableNames:
            for table in re.split(", ", tableNames):
                tableArray.append(table)
        else:
            tableArray.append(tableNames)

    if " " in tableNames:
        tableNames = tableNames.strip("\r") #removes any leftover returns
        tableNames = tableNames.strip() #removes any whitespace

    if "," in tableNames:
        for table in re.split(", ", tableNames):
            table, tableVariable = re.split(" ", table, flags=re.IGNORECASE) #grab the left table name
            table_lookup[tableVariable] = table
            tableArray.append(table)
            tableVariables.append(tableVariable)

        #TableName Parsing section for WHERE statements
        #https://stackoverflow.com/questions/7945182/opening-multiple-an-unspecified-number-of-files-at-once-and-ensuring-they-are

    #Loop through every tableName to make every file path
    for tableName in tableArray:
        if tableName:
            fileNames.append(os.path.join(workingDir, tableName))

    return fileNames, tableVariables, joinType

if __name__ == '__main__':
	main()
