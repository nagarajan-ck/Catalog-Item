# CATALOG ITEM


## ABOUT

Catalog Item application lets you view,add,edit and delete items for many categories. The app lets you do CRUD operations provided you have authenticated yourselves using Facebook. You will need a Google account to use this application.

The application can be viewed on the localhost at port 8000. The app lets you do the following operations.

#### Add

Add as many items as you want to a category, select the name and the category to which it belongs upon creation and give it a suitable description. You will need to log in to add an item.

#### Edit

Edit existing items that was created by you, change its name, move it between categories and save the changes.

#### Delete

Delete an item that was created by you from the inventory altogether.


## REQUIREMENTS

The tool uses **python3** and **SQLAlchemy** for the analysis. It uses **OAuth** for authentication. So it is essential to have python3 with the sqlalchemy library and sql installed on your machine along with OAuth.


# SETTING THE ENVIRONMENT

- Navigate to the Catalog directory. Run the __database_setup.py__ file which creates the database file with the required tables.

`python3 database_setup.py`

- To add data into the table, run the __lotsofmenus.py__ file.

`python3 lotsofmenus.py`

- Now that we have the datas set up, run the server using the following code.

`python3 application.py`

- Open the browser and browse the localhost running at port 8000

`http://localhost:8000`

- Log into the app using Google authentication to execute CRUD operations


## CREDITS

This application uses code from Google OAuth for the authentication process such as the login button. The code has been customised for the suitability of this app.
