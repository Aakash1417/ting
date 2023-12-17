from Login import Login
from Connection import Connection
import datetime


class Follow():
    @staticmethod
    def follow(flwee: int) -> None:
        """Records the currently logged-in user following someone else

        Args:
            flwee (int): the user id of the user to follow
        """
        assert Connection.is_connected()
        query = "SELECT flwer FROM follows, users WHERE flwer = ? AND flwee = ?"
        if (Connection.contains(query, (Login.userID, flwee))):  # already follows the user
            print("You already follow " + Follow.getName(flwee))
        else:
            Connection.cursor.execute("INSERT INTO follows VALUES(?,?,?)",
                                      (Login.userID, flwee, datetime.date.today()))
            print("You started following " + Follow.getName(flwee))
            Connection.connection.commit()
        print()


    @staticmethod
    def getName(usr: int) -> str:
        """Gets the name of a given user

        Args:
            usr (int): the user id of the chosen user

        Returns:
            str: the name of the user
        """
        assert Connection.is_connected()
        Connection.cursor.execute("SELECT name FROM users WHERE usr = ?",
                                  (usr, ))
        result = Connection.cursor.fetchone()
        return result[0]
