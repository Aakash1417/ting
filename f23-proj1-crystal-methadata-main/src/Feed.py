from Connection import Connection
from Login import Login
from Search import Search


class Feed:
    @staticmethod
    def show_feed() -> None:
        """Finds the tweets/retweets of those the user is following, then produces a feed to interact with."""
        assert Connection.is_connected()
        assert Login.userID is not None
        feedQuery = """
            SELECT name, tid, writer, tdate, text, replyto, NULL as retweeter
            FROM users u, tweets t, follows f
            WHERE u.usr = t.writer
                AND t.writer = f.flwee
                AND f.flwer = ?
            UNION
            SELECT u.name, rt.tid, t.writer, rt.rdate, t.text, t.replyto, rt.usr
            FROM users u, retweets rt, tweets t, follows f
            WHERE u.usr = t.writer
                AND t.tid = rt.tid
                AND rt.usr = f.flwee
                AND f.flwer = ?
            ORDER BY t.tdate DESC"""

        Connection.cursor.execute(feedQuery, (Login.userID, Login.userID))
        results = Connection.cursor.fetchall()

        column_names = [description[0]
                        for description in Connection.cursor.description]

        Search.parse_results(results, column_names, 5, [
            "scrollup", "scrolldown", "viewinfo", "reply", "retweet"], 'tweet')


if __name__ == "__main__":
    import os
    from Setup import Setup
    from Test import Test

    path = os.path.dirname(os.path.realpath(__file__)) + "/data.db"
    Connection.connect(path)

    # create tables
    Setup.drop_tables()
    Setup.define_tables()

    Test.insert_test_data()

    Login.userID = 1
    Feed.show_feed()
