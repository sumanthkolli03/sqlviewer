from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import DatabaseError
import os

app = Flask(__name__)


def create_db_list(databases):
    """Method to create the string that returns databases/tables in the html"""
    db_list = []
    for db in databases:
        db_list.append("<option value='" + db[0] + "'>" + db[0] + "</option>")
    db_list_string = "\n".join(db_list)
    return db_list_string

@app.route("/", methods=['GET', 'POST'])
def startpage():
    """Landing page of localhost:5000, sends directly to login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page, attempts to login to mysql.connector"""
    """If Successful, takes you to db_view. If failed, returns to login"""
    print("Login Page")
    global uurl, uport, username, upass
    if request.method == 'POST':
        uurl = request.form.get("uurl")
        uport = request.form.get("port")
        if uport != None:
            uport = int(uport)
        username = request.form.get('username')
        upass = request.form.get('password')
        print("Received:", uurl, uport, username, upass)
        try:
            global connection, databases, cursor, db_list_string
            print("Trying:", uurl, uport, username, upass)
            connection = mysql.connector.connect(
                host = uurl,
                port = uport,
                user = username,
                password = upass
            )
            print("Connected")
            cursor = connection.cursor()
            print("cursor")
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            db_list_string = create_db_list(databases)
            print("fetched databases")
            
        except:
            print("user/pass failed, returning")
            return render_template("login_failed.html")
        else:
            print("user/pass successfully received")
            return redirect(url_for('db_view'))
        #try statement to login to database, if succeeds -> move into render_template(db_view)
    else:
        return render_template('login.html')


@app.route('/db_view', methods=['GET', 'POST'])
def db_view():
    """Lets you choose a database. Selected database redirects to view selected db"""
    global db_list_string, selected_db
    print("db_view page")
    #print(db_list_string)
    if request.method == 'POST':
        selected_db = request.form.get("dbchoose")
        print("You selected:", selected_db)
        return redirect(url_for('view_selected_db'))
    return render_template('db_view.html', db_list_html = db_list_string)

@app.route("/view_selected_db", methods=['GET', 'POST'])
def view_selected_db():
    """Lets you choose a table. Selected table redirects to view selected table."""
    global selected_db, cursor, uurl, uport, username, upass, tablename, tempcursor, tempcnx
    print("view_selected_db page")
    tempcnx = mysql.connector.connect(
                host = uurl,
                port = uport,
                user = username,
                password = upass,
                database = selected_db
            )
    tempcursor = tempcnx.cursor()
    tempcursor.execute("SHOW TABLES")
    table_names_unsort = tempcursor.fetchall()
    table_names = create_db_list(table_names_unsort)
    if request.method == 'POST':
        tablename = request.form.get("tablechoose")
        print("You selected:", tablename)
        return redirect(url_for('view_selected_table'))
    return render_template("selected_db_view.html", table_names_html = table_names, db_name_html=selected_db)

    
@app.route("/view_selected_table", methods=['GET', 'POST'])
def view_selected_table():
    """Table view."""
    global selected_db, cursor, uurl, uport, username, upass, tablename, tempcursor, tempcnx
    print("Viewing", tablename)
    tempcnx = mysql.connector.connect(
                host = uurl,
                port = uport,
                user = username,
                password = upass,
                database = selected_db
            )
    tempcursor = tempcnx.cursor()
    tempcursor.execute(f"SELECT * FROM {tablename} LIMIT 50")
    rows = tempcursor.fetchall()
    column_names = [desc[0] for desc in tempcursor.description]
    return render_template("selected_table.html", tablename = tablename, rows=rows, column_names = column_names)

@app.route("/delete/<string:id>")
def delete(id):
    """Url for delete database. If failed, it keeps database. Redirects to view_selected_table"""
    colname = id.split("_")[0]
    idnum = id.split("_")[1]
    global tempcursor, tempcnx, tablename
    try:
        tempcursor.close()
        tempcursor = tempcnx.cursor()
        tempcursor.execute(f"DELETE FROM {tablename} WHERE {colname} = {idnum}")
        tempcnx.commit()
        print("Successfully deleted row")
        return redirect("/view_selected_table")
    except:
        print(f"Failed to delete row. Check {tablename} table constraints")
        return redirect("/view_selected_table")



@app.route("/dropDB/<string:to_drop_db>")
def dropDB(to_drop_db):
    """Redirects to db_view. Attempts to drop a database."""
    global tempcursor, tempcnx, db_list_string, cursor
    print(f"Attempting to drop {to_drop_db}")
    try:
        print("Attempting to execute query")
        tempcursor.execute(f"DROP DATABASE {to_drop_db}")
        print("Attempting to commit")
        tempcnx.commit()
        print("Successfully dropped")
        tempcursor.execute("SHOW DATABASES")
        databases = tempcursor.fetchall()
        db_list_string = create_db_list(databases)
        return redirect("/db_view")
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        return redirect("/db_view")

@app.route("/dropTable/<string:to_drop_table>")
def dropTable(to_drop_table):
    """Redirects to view_selected_db. Attempts to drop table."""
    global tempcursor, tempcnx
    print(f"Attempting to drop {to_drop_table}")
    try:
        print("Attempting to execute query")
        tempcursor.execute(f"DROP TABLE {to_drop_table}")
        print("Attempting to commit")
        tempcnx.commit()
        print("Successfully dropped")
        return redirect("/view_selected_db")
    except:
        print("Failed to drop")
        return redirect("/view_selected_db")
    
@app.route("/addDB", methods=["GET","POST"])
def addDB():
    """Method to add database and data. Copies file to your local directory,
    Attempts to add it to SQL, then deletes file."""
    global connection, cursor, db_list_string, uurl, uport, username, upass
    if request.method == 'POST':
        try:
            db_file = request.files['db_file']
            db_file.save(db_file.filename)
            print("File saved to local storage.")
        except:
            flash("Failed to upload file")
            return render_template("uploadDB.html")
        try:
            print("Reading File:", db_file.filename)
            with open(db_file.filename, "r") as f:
                print("Attempting to execute queries")
                cursor.close()
                cursor = connection.cursor()
                cursor.execute(f.read(), multi=True)
                cursor.fetchall()
                print("Successfully executed query (commits should be in the .sql file)")
            os.remove(db_file.filename)
            print("File removed from local storage - Succesful Execute")
            connection = mysql.connector.connect(
                host = uurl,
                port = uport,
                user = username,
                password = upass
            )
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            db_list_string = create_db_list(databases)
            return redirect("/db_view")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            os.remove(db_file.filename)
            print("File removed from local storage - Failed to execute")
            return(redirect("/db_view"))
    return render_template("uploadDB.html")



if __name__ == "__main__":
    app.run(debug=True)
