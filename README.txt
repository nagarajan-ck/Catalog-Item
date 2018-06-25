# CATALOG ITEM


## ABOUT

Catalog Item application lets you view,add,edit and delete items for many categories. The app lets you do CRUD operations provided you have authenticated yourselves using Facebook. **Facebook will have permissions to access your public profile only, and the app will not have access to post on Facebook on your behalf.**

The application can be viewed on the localhost at port 8000. The app lets you do the following operations.

#### Add

Add as many items as you want to a category, select the name and the category to which it belongs upon creation and give it a suitable description

#### Edit

Edit existing items, change its name, move it between categories and save the changes.

#### Delete

Delete the item from the inventory altogether.


## REQUIREMENTS

The tool uses **python3** and **SQLAlchemy** for the analysis. So it is essential to have python3 with the sqlalchemy library and sql installed on your machine.


# SETTING THE ENVIRONMENT

- Navigate to the Catalog directory. Run the __database_setup.py__ file which creates the database file with the required tables.

`python3 database_setup.py`

- To add data into the table, run the __lotsofmenus.py__ file.

`python3 lotsofmenus.py`

- Now that we have the datas set up, run the server using the following code.

`python3 application.py`

- Open the browser and browse the localhost running at port 8000

`http://localhost:8000`

- Log into the app using Facebook authentication to execute CRUD operations


## CREDITS

This application uses code from Facebook for the authentication process such as async loads for the pages and the login button. The code has been customised for the suitability of this app.
