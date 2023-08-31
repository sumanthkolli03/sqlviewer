Steps to run:
    Try opening with the `start windows.bat` or using `start mac.sh`.
    I have a PC, so I can only test the `start windows.bat`.
    If it fails, do the following:

* open terminal or cmd 
* cd to the folder that contains app.py
* type the following (without the quotes)
Windows: 
* `env\Scripts\activate`
* `pip install -r requirements.txt`
* `python app.py`
Mac: 
* `env/Scripts/activate` or equivalent that'll open the virtual environment
* `pip install -r requirements.txt` or equivalent that'll install requirements
* `python3 app.py` or equivalent that'll run app.py

Again, mac is untested, so the gist is to open the venv, install the requirements, and run app.py.

To Use:
    Make sure the mysql service is running on your PC.
    Open your browser and type localhost:5000
    Login to your MYSQL connection (defaults are there to run off your own machine)


App.py is documented, but the general flowchart is as follows:
localhost:5000 (landing page) -> autoredirects to login

login if successfull -> db_view
login if failed -> login

db_view -> choose database -> view_selected_db
db_view -> Add Schema or Data -> upload file -> attempt to add -> db_view

view_selected_db -> choose table -> view_selected_table
view_selected_db -> Drop Database -> attempts to drop database -> db_view

view_selected_table ->  you can view the first 50 rows. Delete attempts to drop a row (this is held back by table constraints), and returns to the table view.
view_selected_table -> Drop Table -> attempts to drop table (held back by constraints) -> view_selected_db

"# sqlviewer" 
