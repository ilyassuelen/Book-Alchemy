from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os
from data_models import db, Author, Book
import google.generativeai as genai
from dotenv import load_dotenv

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


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return "Book not found", 404

    author = book.author

    db.session.delete(book)
    db.session.commit()

    message = f'"{book.title}" was deleted successfully!'

    # If the book’s author doesn’t have any other books in your library → delete
    if len(author.books) == 0:
        db.session.delete(author)
        db.session.commit()
        message += f' Author "{author.name}" deleted as well.'

    sort = request.args.get("sort", "title")
    return redirect(url_for('home', message=message, sort=sort))


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@app.route("/recommend")
def recommend():
    books = Book.query.all()
    if not books:
        return render_template("recommend.html", recommendation="No books found. Add some first!")

    # Liste der Buchtitel + Autoren generieren
    book_list_text = "\n".join([f"{book.title} by {book.author.name}" for book in books])

    prompt = f"""
    I have read the following books:
    {book_list_text}

    Based on this list, recommend one new amazing book I should read next.
    Explain briefly why you recommend it.
    """

    model = genai.GenerativeModel("models/gemini-pro-latest")
    response = model.generate_content(prompt)

    recommendation = response.text if response.text else "Could not generate recommendation."

    return render_template("recommend.html", recommendation=recommendation)


"""# Create tables
with app.app_context():
  db.create_all()"""


if __name__ == "__main__":
    app.run(debug=True)