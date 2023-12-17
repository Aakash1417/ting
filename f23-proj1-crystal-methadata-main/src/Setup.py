from Connection import Connection


class Setup:
    @staticmethod
    def drop_tables() -> None:
        """Runs a query to drop all existing tables in the db"""
        assert Connection.is_connected()

        dropQuery = """
        DROP TABLE IF EXISTS includes;
        DROP TABLE IF EXISTS lists;
        DROP TABLE IF EXISTS retweets;
        DROP TABLE IF EXISTS mentions;
        DROP TABLE IF EXISTS hashtags;
        DROP TABLE IF EXISTS tweets;
        DROP TABLE IF EXISTS follows;
        DROP TABLE IF EXISTS users;
        """
        Connection.cursor.executescript(dropQuery)


    def define_tables() -> None:
        """Runs a query to create new tables in db according to project spec"""
        assert Connection.is_connected()

        defineQuery = """
        CREATE TABLE IF NOT EXISTS users (
            usr         INT,
            pwd         TEXT,
            name        TEXT,
            email       TEXT,
            city        TEXT,
            timezone    FLOAT,
            PRIMARY KEY (usr)
        );
        CREATE TABLE IF NOT EXISTS follows (
            flwer       INT,
            flwee       INT,
            start_date  DATE,
            PRIMARY KEY (flwer, flwee),
            FOREIGN KEY (flwer) REFERENCES users,
            FOREIGN KEY (flwee) REFERENCES users
        );
        CREATE TABLE IF NOT EXISTS tweets (
            tid         INT,
            writer      INT,
            tdate       DATE,
            text        TEXT,
            replyto     INT,
            PRIMARY KEY (tid),
            FOREIGN KEY (writer) REFERENCES users,
            FOREIGN KEY (replyto) REFERENCES tweets
        );
        CREATE TABLE IF NOT EXISTS hashtags (
            term        TEXT,
            PRIMARY KEY (term)
        );
        CREATE TABLE IF NOT EXISTS mentions (
            tid         INT,
            term        TEXT,
            PRIMARY KEY (tid, term),
            FOREIGN KEY (tid) REFERENCES tweets,
            FOREIGN KEY (term) REFERENCES hashtags
        );
        CREATE TABLE IF NOT EXISTS retweets (
            usr         INT,
            tid         INT,
            rdate       DATE,
            PRIMARY KEY (usr, tid),
            FOREIGN KEY (usr) REFERENCES users,
            FOREIGN KEY (tid) REFERENCES tweets
        );
        CREATE TABLE IF NOT EXISTS lists (
            lname       TEXT,
            owner       INT,
            PRIMARY KEY (lname),
            FOREIGN KEY (owner) REFERENCES users
        );
        CREATE TABLE IF NOT EXISTS includes (
            lname       TEXT,
            member      INT,
            PRIMARY KEY (lname, member),
            FOREIGN KEY (lname) REFERENCES lists,
            FOREIGN KEY (member) REFERENCES users
        );
        """
        Connection.cursor.executescript(defineQuery)
        Connection.connection.commit()
