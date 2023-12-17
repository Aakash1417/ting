import os
from Connection import Connection
from Setup import Setup


class Test:
    @staticmethod
    def insert_test_data() -> None:
        """Populates all the db tables with mock data"""
        assert Connection.is_connected()

        # Insert sample data into the 'users' table
        users_data = [
            (1, 'password1', 'User1', 'user1@example.com', 'City1', 1.0),
            (2, 'password2', 'User2', 'user2@example.com', 'City2', 2.0),
            (3, 'password3', 'User3', 'user3@example.com', 'City3', 3.0),
        ]
        Connection.cursor.executemany(
            "INSERT INTO users VALUES (?,?,?,?,?,?)", users_data)

        follows_data = [
            (1, 2, '2023-01-01'),
            (2, 1, '2023-01-02'),
            (1, 3, '2023-01-03'),
            (3, 2, '2023-01-04'),
        ]
        Connection.cursor.executemany(
            "INSERT INTO follows VALUES (?,?,?)", follows_data)

        # Insert sample data into the 'tweets' table
        tweets_data = [
            (1, 1, '2023-01-01', 'This is a tweet by User1 #another', None),
            (2, 2, '2023-01-02', '#Another tweet by User2', None),
            (3, 3, '2023-01-03', 'Tweet from User3', 1),
        ]
        Connection.cursor.executemany(
            "INSERT INTO tweets VALUES (?,?,?,?,?)", tweets_data)

        # Insert sample data into the 'hashtags' table
        hashtags_data = [
            ('example1',),
            ('example2',),
            ('sample',),
            ('test',),
            ('another',),
            ('thingy',),
        ]
        Connection.cursor.executemany(
            "INSERT INTO hashtags VALUES (?)", hashtags_data)

        # Insert sample data into the 'mentions' table
        mentions_data = [
            (1, 'example1'),
            (2, 'example2'),
            (3, 'sample'),
            (1, 'test'),
            (1, 'another'),
            (2, 'another'),
            (2, 'thingy'),
        ]
        Connection.cursor.executemany(
            "INSERT INTO mentions VALUES (?,?)", mentions_data)

        # Insert sample data into the 'retweets' table
        retweets_data = [
            (1, 2, '2023-01-03'),
            (2, 1, '2023-01-04'),
            (3, 1, '2023-01-05'),
        ]
        Connection.cursor.executemany(
            "INSERT INTO retweets VALUES (?,?,?)", retweets_data)

        # Insert sample data into the 'lists' table
        lists_data = [
            ('List1', 1),
            ('List2', 2),
            ('List3', 1),
        ]
        Connection.cursor.executemany(
            "INSERT INTO lists VALUES (?,?)", lists_data)

        # Insert sample data into the 'includes' table
        includes_data = [
            ('List1', 2),
            ('List2', 1),
            ('List3', 3),
        ]
        Connection.cursor.executemany(
            "INSERT INTO includes VALUES (?,?)", includes_data)

        Connection.connection.commit()


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__)) + "/data.db"
    Connection.connect(path)

    # create tables
    Setup.drop_tables()
    Setup.define_tables()

    Test.insert_test_data()
