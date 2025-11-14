from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.String)
    date_of_death = db.Column(db.String)

    # Relationship
    books = db.relationship("Book", back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.name} (born: {self.birth_date}, died: {self.date_of_death})"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.Integer)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.String)

    # Foreign key to Author
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))

    # Relationship back to Author
    author = db.relationship("Author", back_populates="books")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"

    def __str__(self):
        return f"{self.title} (ISBN: {self.isbn}, Year: {self.publication_year})"
