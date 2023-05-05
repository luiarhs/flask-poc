DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS question;

CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT UNIQUE NOT NULL
);

CREATE TABLE question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    question TEXT UNIQUE NOT NULL,
    answer TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category (id)
);

INSERT INTO category (type)
VALUES
    ("Science"),
    ("Art"),
    ("Geography"),
    ("History"),
    ("Entertainment"),
    ("Sports");

INSERT INTO question (category_id, question, answer, difficulty)
VALUES
    (1, "What is the heaviest organ in the human body?", "The liver", 4),
    (1, "Who discovered penicillin?", "Alexander Fleming", 4),
    (1, "Hematology is a branch of medicine involving the study of what?", "Blood", 2),
    (2, "Which Dutch graphic artist, initials M C, was a creator of optical illusions?", "Escher", 1),
    (2, "La Giaconda is better known as what?", "Mona Lisa", 3),
    (2, "How many paintings did Van Gogh sell in his lifetime?", "One", 4),
    (2, "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?", "Jackson Pollock", 2),
    (3, "What is the largest lake in Africa?", "Lake Victoria", 2),
    (3, "In which royal palace would you find the Hall of Mirrors?", "The Palace of Versailles", 3),
    (3, "The Taj Mahal is located in which Indian city?", "Agra", 2),
    (4, "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?", "Maya Angelou", 2),
    (4, "What boxer's original name is Cassius Clay?", "Muhammad Ali", 1),
    (4, "Who invented peanut butter?", "George Washington Carver", 2),
    (4, "Which dung beetle was worshipped by the ancient Egyptians?", "Scarab", 4),
    (5, "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?", "Apollo 13", 4),
    (5, "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?", "Tom Cruise", 4),
    (5, "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?", "Edward Scissorhands", 3),
    (6, "Which is the only team to play in every soccer World Cup tournament?", "Brazil", 3),
    (6, "Which country won the first ever soccer World Cup in 1930?", "Uruguay", 4);
    