# Library-Management-System
A basic library management system webapp made using Python, Flask, MySQL, SQLAlchemy, HTML and CSS.


## Introduction
The Library Management System webapp is a simple webapp that allows for admin and user access to the library portal. \
The admin can make changes to the system, including creation and modification of books and sections and management of requests (accepting and rejecting requests). The admin also has access to purchases data for the users as well as graphical representation of the most popular books in the library based on the number of requests and average ratings given by the users. \
The user can browse the entire book catalogue hosted by the library or segregate books by sections. The user can also search the book catalogue on the basis of the book name, description, section and author. In addition the user can request books for online reading or purchase available books for reading offline. The users can also leave ratings and text reviews for the books that they have purchased or requested.


## Requirements
1. All the required packages are listed in the requirements.txt file.
2. Git
3. DB Browser for SQLite


## Installation and running
In order to run the application on your system follow these steps: \
    1. Clone the repository to your system: \
            ` git clone https://github.com/winpower21/Library-Management-System` \
    2. Change directory to Library-Management-System \
            ` cd  Library-Management-System ` \
    3. Install the required packages: \
            ` pip install -r requirements.txt ` \
    4. Run the app: \
            ` python app.py `

## Note:
In order to access the admin backend login using the admin login form using the following default credentials: \
Email = admin@email.com \
Password = admin \
To create your own admin, register the admin user using the register link on the user login form, and then use DB Browser to change the user type for that user to ***admin***.
