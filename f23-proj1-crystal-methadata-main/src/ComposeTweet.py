import os
import string
import datetime

from Connection import Connection
from Login import Login
from Test import Test
from Setup import Setup


class ComposeTweet:
    @staticmethod
    def countTweets() -> int:
        """Counts the number of tweets and finds maximum tid

        Returns:
            int: maximum tid, or 0 if there are no tweets
        """
        assert Connection.is_connected()
        query = "SELECT MAX(tid) FROM tweets"
        Connection.cursor.execute(query)
        entry = Connection.cursor.fetchone()

        if entry[0] is None:
            return 0
        else:
            return entry[0]


    @staticmethod
    def createTweet(replyTo: int = None) -> None:
        """Prompts the user to create a new tweet/reply and adds it to the db

        Args:
            replyTo (int, optional): the tweet id that to reply to. Defaults to None.
        """
        tweet = ""
        # checks if it is a tweet or reply (checks if tweet being replied to exists)
        if replyTo == None:
            tweet = input("Enter tweet message: ")
        elif Connection.contains("SELECT tid FROM tweets WHERE tid = ?;", (replyTo,)):
            tweet = input("Enter reply: ")
        else:
            print("Parent tweet does not exist.\n")
            return

        if tweet == "":
            print("Empty tweet text. Cancelling compose.\n")
            return

        tid = ComposeTweet.countTweets() + 1  # the tid for new tweet/reply
        ComposeTweet.addTweetToTweetsDB(tid, tweet, replyTo)


    @staticmethod
    def createRetweet(tid: int) -> None:
        """Attempts to retweet a given tweet

        Args:
            tid (int): the tweet id to retweet
        """
        if Connection.contains("SELECT tid FROM retweets WHERE tid = ? AND usr = ?;", (tid, Login.userID)): 
            print("You have already retweeted this tweet.")
        else:
            ComposeTweet.addRetweetToDB(tid)
            print("Your retweet has successfully been posted! ")

   
    @staticmethod
    def addTweetToTweetsDB(tid: int, tweet: str, replyTo: int) -> None:
        """Adds a new tweet to the tweets table in the db

        Args:
            tid (int): the new tweet id
            tweet (str): the content of the tweet
            replyTo (int): the tid of tweet to reply to (None if not replying)
        """
        assert Connection.is_connected()
        insert_query = "INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, ?, ?, ?)"
        Connection.cursor.execute(
            insert_query, (tid, Login.userID, datetime.date.today(), tweet, replyTo))
        Connection.connection.commit()

        if replyTo == None:
            print("Your tweet has successfully been posted!")
        else:
            print("Your reply has successfully been posted!")

        ComposeTweet.findHashTags(tid, tweet)


    @staticmethod
    def findHashTags(tid: int, text: str) -> None:
        """Finds all the hashtags in a new tweet text, adding to the db as necessary

        Args:
            tid (int): the tweet id of the new tweet
            text (str): the text that is checked for any hashtags
        """
        words = text.split()
        hashtags = []
        for word in words:
            if word[0].startswith("#"):
                for i in range(1, len(word)):
                    # will process characters after '#' before any punctuations
                    # assumptions is that hashtags are alphanumeric
                    if word[i] in string.punctuation:
                        word = word[:i]
                        break
                hashtags.append(word[1:].lower())
        if len(hashtags) > 0:
            for hashtag in hashtags:
                ComposeTweet.addHashtagsToHashtagsDB(hashtag)
                ComposeTweet.addHashtagsToMentionsDB(tid, hashtag)


    @staticmethod
    def addHashtagsToHashtagsDB(hashtag: str) -> None:
        """Adds new hashtag term to hashtags table

        Args:
            hashtag (str): term to add
        """
        assert Connection.is_connected()
        # Check if the hashtag exists in DB
        query = "SELECT term FROM hashtags WHERE term = ?;"
        containsDuplicate = Connection.contains(query, (hashtag,))

        if not containsDuplicate:  # hashtag does not exist
            insert_query = "INSERT INTO hashtags (term) VALUES (?);"
            Connection.cursor.execute(insert_query, (hashtag,))

        Connection.connection.commit()


    @staticmethod
    def addHashtagsToMentionsDB(tid: int, hashtag: str) -> None:
        """Adds new hashtag term and the tweet id to mentions table

        Args:
            tid (int): the tweet id
            hashtag (str): the hashtag term found in the tweet
        """
        assert Connection.is_connected()
        query = "SELECT tid, term FROM mentions WHERE tid = ? AND term = ?;"
        containsDuplicate = Connection.contains(query, (tid, hashtag))

        if not (containsDuplicate):  # tweet doesn't contain the same hashtag
            insert_query = 'INSERT INTO mentions (tid, term) VALUES (?, ?);'
            Connection.cursor.execute(insert_query, (tid, hashtag))
        Connection.connection.commit()

    
    @staticmethod
    def addRetweetToDB(tid: int) -> None:
        """Adds a retweet of a given tweet for the currently logged-in user

        Args:
            tid (int): the tweet id to retweet
        """
        assert Connection.is_connected()
        insert_query = "INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, ?)"
        Connection.cursor.execute(insert_query, (Login.userID, tid, datetime.date.today()))
        Connection.connection.commit()


def test() -> None:
    """Creates test tables"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/data.db"
    Connection.connect(path)
    Setup.drop_tables()
    Setup.define_tables()
    Test.insert_test_data()


if __name__ == "__main__":

    test()

    # manually enter User ID
    usr = input("User ID: ")
    Login.userID = int(usr)

    while (True):
        code = input("tweet/reply <tid>?")
        inputs = code.split()
        if (inputs[0] == "tweet" and len(inputs) == 1):
            ComposeTweet.createTweet()
        elif (inputs[0] == "reply" and inputs[1].isnumeric() and len(inputs) == 2):
            ComposeTweet.createTweet(int(inputs[1]))
        elif (inputs[0] == "exit"):
            break
        else:
            print("INVALID COMMAND -_-")

        Connection.close()
