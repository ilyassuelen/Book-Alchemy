from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os
from data_models import db, Author, Book

# Create a Flask app instance
app = Flask(__name__)

# Configure SQLite database using absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

# Initialize Flask app for SQLAlchemy
db.init_app(app)


@app.route("/add_author", methods=['GET', 'POST'])
def add_author():
    if request.method == "POST":
        name = request.form.get("name")
        birth_date = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")

        # Create new author entry
        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        db.session.add(new_author)
        db.session.commit()

        # Send success message back to the page
        message = "Author added successfully!"
        return render_template("add_author.html", message=message)

    return render_template("add_author.html")


@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == "POST":
        title = request.form.get("book_title")
        isbn = request.form.get("isbn")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        # Create new book entry
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        # Send success message back to the page
        message = "Book added successfully!"
        return render_template("add_book.html", authors=authors, message=message)

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


@app.route("/")
def home():
    sort = request.args.get("sort", "title")
    search = request.args.get("search", "")

    # Basic query
    query = Book.query.join(Author)

    if search:
        keyword = f"%{search}%"
        query = query.filter(
            or_(Book.title.ilike(keyword),
                Author.name.ilike(keyword))
        )

    if sort == "author":
        query = query.order_by(Author.name.asc())
    elif sort == "year":
        query = query.order_by(Book.publication_year.asc())
    else:
        query = query.order_by(Book.title.asc())

    books = query.all()
    return render_template("home.html", books=books, sort=sort)

"""# Create tables
with app.app_context():
  db.create_all()"""

if __name__ == "__main__":
    app.run()