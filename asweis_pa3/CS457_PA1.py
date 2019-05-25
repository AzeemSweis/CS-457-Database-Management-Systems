import os

def useEnabled():
    if globalScopeDirectory is "":
        raise ValueError("Failure to use table because no database is selected.")

try:
    globalScopeDirectory = "" #created for increased scope

    while(True): #this will exit the loop at the end of the function or .EXIT command
        command = raw_input("\n Enter a command \n") #reads input from a terminal

        if ";" in command:
            command = command[:-2]

        if "--" in command: #pass the comments
            pass

        elif "CREATE DATABASE" in command:
            try:
                directory = command.split("CREATE DATABASE ")[1] #store the string after CREATE DATABASE
                if not os.path.exists(directory): #only create if non existant
                    os.makedirs(directory)
                    print("Database " + directory + " created.")
                else:
                    print("!Failed to create database " + directory + "because it already exists.")
            except IndexError:
                print ("Error: No database name specified.")

            elif "DROP DATABASE" in command:
                try:
                    directory = command.split("DROP DATABASE ")[1]
                    IF os.path.exists(directory):
                    for toRemove in os.listdir(directory):
                        os.remove(directory + "/" + toRemove)
                    os.rmdir(directory)
                    print ("Database " + directory + " deleted.")
                else:
                    print ("!Failed to delete database " + directory + " because it does not exist")
                except IndexError:
                    print ("Error: No database name specified")

            elif "USE" in command:
                try:
                    globalScopeDirectory = command.split("USE ")[1]
                    if os.path.exists(globalScopeDirectory):
                        print ("Using database " + globalScopeDirectory + " .")
                    else:
                        raise ValueError("!Failed to use database because it does not exist.")
                except IndexError:
                    print ("!No database name specified")
                excpet ValueError as err:
                print err.args[0]

            elif "CREATE TABLE" in command:
                try:
                    useEnabled()
                    subDirectory = command.split("CREATE TABLE ")[1]
                    subDirectory = subDirectory.split(" (")[0]
                    workingDirectory = os.path.join(os.getcwd(),globalScopeDirectory)
                    fileName = os.path.join(workingDirectory,subDirectory)
                    if not os.path.isfile(fileName):
                        with open(fileName, "w") as table:
                            print ("Table " + subDirectory + " created.")
                            if "(" in command:
                                out = []
                                data = command.split("(",1)[1]
                                data = data[:-1]
                                loopCount = data.count(",")
                                for x in range(loopCount+1):
                                    out.append(data.split(",")[x])
                                table.write( ",".join(out) )
                    else:
                        print ("!Failed to create table " + subDirectory + " because it already exists.")
                except IndexError:
                    print ("!Failed to remove Table because no table name is specified.")
                except ValueError as err:
                    print err.args[0]

            elif "DROP TABLE" in command:
                try:
                    useEnabled()
                    subDirectory = command.split("DROP TABLE ")[1]
                    workingDirectory = os.path.join(os.getcwd(),globalScopeDirectory)
                    filepath = os.path.join(workingDirectory, subDirectory)
                    if os.path.isfile(filePath):
                        os.remove(filePath)
                        print ("Table " + subDirectory + " deleted.")
                    else:
                        print ("!Failed to delete Table " + subDirectory + " because it does not exist.")
                except IndexError:
                    print ("!failed to remove table because no table name is specified.")
                except ValueError as err:
                    print err.args[0]

            elif "SELECT *" in command:
                try:
                    useEnabled()
                    tableName = command.split("FROM ")[1]
                    workingDirectory = os.path.join(os.getcwd(),globalScopeDirectory)
                    fileName = os.path.join(workingDirectory, tableName)
                    if os.path.isfile(fileName):
                        with open(fileName, "r+") as table:
                            output = table.read()
                            print output
                    else:
                        print ("!Failed to query table " + tableName + " because it does not exist")
                except IndexError:
                    print ("!Failed to remove table because no table name is specified")
                except ValueError as err:
                    print err.args[0]

            elif "ALTER TABLE" in command:
                try:
                    useEnabled()
                    tableName = command.split("ALTER TABLE ")[1]
                    tableName = tableName.split(" ")[0]
                    workingDirectory = os.path.join(os.getcwd(), globalScopeDirectory)
                    fileName = os.path.join(workingDirectory, tableName)
                    if os.path.isfile(fileName):
                        if "ADD" in command:
                            with open(fileName, "a") as table:
                                additionalString = command.split("ADD ")[1]
                                table.write(", " + additionalString)
                                print ("Table " + tableName + " modified.")
                    else:
                        print ("!Failed to alter table " + tableName + " because it does not exist.")
                except IndexError:
                    print ("!Failed to remove Table because no table name is specified.")
                except ValueError:
                    print err.args[0]

            elif ".EXIT" in command:
                print ("All done.")
                exit()

except (EOFError, KeyboardInterrupt) as e:
    print ("\nConnection to database terminated.")
