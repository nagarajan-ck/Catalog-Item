from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
import requests
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from flask import session as login_session


app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db',connect_args={'check_same_thread':False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def homepage():
    item = session.query(Item).order_by(Item.id.desc()).limit(10).all()
    category = session.query(Category).all()
    return render_template("homepage.html", item = item, category= category)




@app.route('/catalog/<category>/Items/')
@app.route('/catalog/<category>/')
def category_page(category):
    cat_id = session.query(Category).filter_by(name = category).one().id
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(category_id=cat_id).all()
    count = len(item)
    return render_template('category_page.html',category=category, item=item, categories = categories,count=count )


@app.route('/catalog/<category>/<item>/')
def item_page(category,item):
    desc= session.query(Item).filter_by(title = item).one().description
    return render_template('item_page.html',desc=desc,item=item)


@app.route('/catalog/add', methods=['GET','POST'])
def add_item():
    if(request.method=='GET'):
        full_categories= session.query(Category).all()
        return render_template('add_item.html', full_categories=full_categories)

    else:
        category_id= session.query(Category).filter_by(name=request.form['Category']).one().id
        item = Item(title=request.form['Title'],description=request.form['Description'], category_id=category_id)
        session.add(item)
        session.commit()
        return redirect(url_for('homepage'))



@app.route('/catalog/<item>/edit', methods=['GET','POST'])
def edit_item(item):
    item_to_edit= session.query(Item).filter_by(title = item).one()
    if (request.method=='GET'):
        full_categories = session.query(Category).all()
        current_category = session.query(Category).filter_by(id=item_to_edit.category_id).one().name
        return render_template('edit_item.html', item_to_edit=item_to_edit, full_categories=full_categories, current_category=current_category)
    else:
        item_to_edit.title = request.form['Title']
        item_to_edit.description = request.form['Description']
        item_to_edit.category_id = session.query(Category).filter_by(name=request.form['Category']).one().id
        return redirect(url_for('category_page',category=request.form['Category']))


@app.route('/catalog/<item>/delete/', methods=['GET','POST'])
def delete_item(item):
    item_to_delete=session.query(Item).filter_by(title=item).one()
    category=session.query(Category).filter_by(id=item_to_delete.category_id).one()
    if(request.method=='GET'):
        return render_template('delete_item.html',item=item_to_delete, category=category)
    else:
        session.delete(item_to_delete)
        session.commit()
        print(category.name)
        return redirect(url_for('category_page',category=category.name))


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
