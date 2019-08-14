import sqlite3
import datetime


##################################################
#                                                #
#                   my_logger                    #
#                                                #
#   to use  - import function in your program    #
#           - record your log with parameters    #
#           - enjoy !!!                          #
#                                                #
##################################################


# message is just plain text
# severity can be any warning system you choose
#   such as : "Info", "Warning", "Error", "System", ...


# this is for logging into a sqlite3 database
# with this this system, you don't have to install additional librairies
def log_db(message, severity = "Info"):
    try:
        with sqlite3.connect("log.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT datetime, severity, message FROM log ORDER BY datetime DESC LIMIT 1")
                #print("database already created and ready !")
            except Exception:
                cursor.execute("CREATE TABLE log(ID INTEGER PRIMARY KEY AUTOINCREMENT, datetime TEXT NOT NULL, severity TEXT NOT NULL, message TEXT NOT NULL);")
                conn.commit()
                #print("database created and ready!")
            finally:
                query = "INSERT INTO log (datetime, severity, message) VALUES (?,?,?)"
                sql_input = (datetime.datetime.now(), str(severity), str(message))
                cursor.execute(query, sql_input)
                conn.commit()
    except Exception as e:
        conn.rollback()
        print("oups, something went wrong in log_db -> {}".format(e))


# this is for logging into a text file
# with this this system, you don't have to install additional librairies
def log_file(message, severity="Info"):
    try:
        with open ("log.txt", "a") as fic:
            fic.write("{} ; {} ; {}\n".format(datetime.datetime.now(), str(severity), str(message)))
            #print("data saved")
    except Exception as e:
        print("oups, something went wrong in log_file -> {}".format(e))


if __name__ == "__main__":
    #log_file("Info", "everything went smooth...")
    #log_file("Warning", "everything went wrong!!!!")
    #log_db("Info", "prepared query works !!")
    log_file("everything went smooth...")
