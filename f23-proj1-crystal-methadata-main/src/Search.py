import math
from Connection import Connection
from Setup import Setup
from Login import Login
from Follow import Follow


class Search:
    @staticmethod
    def search_for_tweets() -> None:
        """Prompts for keywords to search tweets by (text+mentions) and displays the results.
            Provides various options for interacting with the results (ie. a tweets activity)
        """
        while True:
            keywords = input(
                "Enter keywords to search for (separate multiple keywords with spaces): ").strip().lower().split()
            if len(keywords) == 0:
                print("Please enter at least one keyword.")
            else:
                break

        conditions = []
        params = []
        tables = set(["tweets t", "users u"])
        for keyword in keywords:
            if keyword.startswith("#"):
                tables.add("mentions m")
                term = keyword[1:]
                conditions.append("(LOWER(m.term) = ? AND m.tid = t.tid)")
                params.append(term)
            else:
                conditions.append("(LOWER(t.text) LIKE ?)")
                params.append('%' + keyword + '%')

        table_clause = ", ".join(tables)
        where_clause = " OR ".join(conditions)

        query = f"""
            SELECT DISTINCT u.name, t.tid, t.writer, t.tdate, t.text, t.replyto, NULL as retweeter
            FROM {table_clause}
            WHERE ({where_clause})
            AND u.usr = t.writer
            ORDER BY t.tdate DESC;"""

        Connection.cursor.execute(query, params)
        results = Connection.cursor.fetchall()

        column_names = [description[0]
                        for description in Connection.cursor.description]

        Search.parse_results(results, column_names, 5, [
            "scrollup", "scrolldown", "viewinfo", "reply", "retweet"], 'tweet')


    @staticmethod
    def search_for_user_tweets(usr: int) -> None:
        """Searches for the tweets of a given user and presents a tweets activity.
        
        Args:
            usr (int): the user id of the selected user
        """
        query = f"""
            SELECT DISTINCT u.name, t.tid, t.writer, t.tdate, t.text, t.replyto, NULL as retweeter
            FROM users u, tweets t
            WHERE u.usr = t.writer
            AND t.writer = ?
            ORDER BY t.tdate DESC;"""   
            
        Connection.cursor.execute(query, (usr,))
        results = Connection.cursor.fetchall()

        column_names = [description[0]
                        for description in Connection.cursor.description]
        Search.parse_results(results, column_names, 3, [
            "scrollup", "scrolldown", "viewinfo", "reply", "retweet"], 'tweet')   

    
    @staticmethod
    def search_for_users() -> None:
        """Prompts for keywords to search users by (name+city) and displays the results.
            Provides various options for interacting with the results (ie. a users activity)
        """
        assert Connection.is_connected()
        keyword = []
        while True:
            # ensure that only one keyword is entered
            keyword =  input("Enter a keyword to search users for: ").strip().split()
            if len(keyword) != 1:
                print("Please enter only one (1) keyword")
            else:
                break

        # users whose name match are shown in ascending order of name length first
        # then, remaining users by ascending order of city length
        query = """
            SELECT DISTINCT usr, name, city
            FROM users
            WHERE LOWER(name) LIKE '%' || LOWER(?) || '%' 
            OR LOWER(city) LIKE '%' || LOWER(?) || '%'
            ORDER BY
                (CASE
                    WHEN LOWER(name) LIKE '%' || LOWER(?) || '%' THEN 1
                    ELSE 2
                END),
                (CASE
                    WHEN LOWER(name) LIKE '%' || LOWER(?) || '%' THEN LENGTH(name)
                    ELSE LENGTH(city)
                END);"""
        Connection.cursor.execute(query, (keyword[0], keyword[0], keyword[0], keyword[0]))
        results = Connection.cursor.fetchall()

        column_names = [description[0]
                        for description in Connection.cursor.description]

        Search.parse_results(results, column_names, 5,
                            ["scrollup", "scrolldown", "select", "follow"], 'user')


    @staticmethod
    def search_for_followers() -> None:
        """Searches for all followers of currently logged in user,
            displaying results in a users activity.
        """
        assert Connection.is_connected()
        # users whose follow the logged in user in ordered in descending date followed
        query = "SELECT DISTINCT usr, name, city FROM follows, users WHERE flwee = ? AND flwer = usr ORDER BY start_date DESC"
        Connection.cursor.execute(query, (Login.userID,))
        results = Connection.cursor.fetchall()

        column_names = [description[0]
                        for description in Connection.cursor.description]

        Search.parse_results(results, column_names, len(results), [
                             "scrollup", "scrolldown", "select", "follow"], 'user')


    @staticmethod
    def parse_results(query_results: [tuple], column_names: [str], num_display: int, additional_options: [str], item_type: str) -> None:
        """Parses query results (a list of tuples ie. rows),
            converting to a list of dictionaries (keys are column names)
            and passes it to interact()

        Args:
            query_result (list[tuple]): the query results
            column_names (list[str]): the names of the columns returned for query results
            num_display (int): number of tweets/user to display at once
            additional_options (list[str]): the additional commands after searching tweets/users
            item_type (str): the type of items being displayed (user/tweet)
        """
        result_list = []
        for row in query_results:
            row_dict = dict(zip(column_names, row))
            result_list.append(row_dict)
        Search.interact(result_list, num_display,
                        additional_options, item_type)


    @staticmethod
    def interact(lst: [dict], num_display: int, additional_options: [str], item_type: str) -> None:
        """Provides options for interacting with the results of a search via a phony shell

        Args:
            lst (list[dict]): A list of tweet/user objects
            num_display (int): The number of tweets/users to display per page
            additional_options (list[str]): A list of additional commands that can be run by the phony shell
            item_type (string): The type of item being displayed (tweet or user)
        """
        offset = 0
        print_options = True

        # run a dummy shell with updated commands for as long as user is here
        while True:
            if print_options:
                Search.print_items(lst, num_display, offset, item_type)

            cmd = input(">>> ").strip().lower().split()
            if len(cmd) < 1:
                print("INVALID COMMAND -_-")
                continue
            print_options = True

            from Shell import Shell
            if cmd[0] in Shell.get_main_options():
                # global commands
                Shell.main_menu_do(
                    cmd[0], additional_options)
                if (cmd[0] != "help"):
                    return
                else:
                    print_options = False
                    continue
            elif cmd[0] == 'scrolldown' and len(cmd) == 1:
                if offset + num_display < len(lst):
                    offset += num_display
            elif cmd[0] == 'scrollup' and len(cmd) == 1:
                offset = max(offset - num_display, 0)
            # follow a selected user
            elif cmd[0] == 'follow' and item_type == 'user':
                try:
                    index = int(cmd[1])
                    # select user by the position of where they appear in a list
                    if index > len(lst)+1 or index < 1:
                        print("INVALID INDEX")
                        continue
                    usr = lst[index-1]['usr']
                    Follow.follow(usr)
                    print_options = False
                except:
                    print("INVALID INDEX")
                    continue
            # select a user to display their information (launching a tweets activity)
            elif cmd[0] == 'select' and item_type == 'user':
                print_options = False
                try:
                    index = int(cmd[1])
                    # select user by the position of where they appear in a list
                    if index > len(lst)+1 or index < 1:
                        print("INVALID INDEX")
                        continue
                    usr = lst[index-1]['usr']
                    Search.get_user_info(usr, lst[index-1]['name']) # displays user info
                    Search.search_for_user_tweets(usr) # displays tweets of users
                    return
                except:
                    print("INVALID INDEX")
                    continue
            # reply to the numbered tweet
            elif cmd[0] == 'reply' and item_type == 'tweet' and len(cmd) == 2:
                print_options = False
                tid = Search.listnum_to_tid(lst, cmd[1])
                if tid is None:
                    print("INVALID INDEX")
                    continue
                from ComposeTweet import ComposeTweet
                ComposeTweet.createTweet(tid)
            # retweet the numbered tweet
            elif cmd[0] == 'retweet' and item_type == 'tweet' and len(cmd) == 2:
                print_options = False
                tid = Search.listnum_to_tid(lst, cmd[1])
                if tid is None:
                    print("INVALID INDEX")
                    continue
                from ComposeTweet import ComposeTweet
                ComposeTweet.createRetweet(tid)
            # view info of a tweet
            elif cmd[0] == 'viewinfo' and item_type == 'tweet' and len(cmd) == 2:
                print_options = False
                tid = Search.listnum_to_tid(lst, cmd[1])
                if tid is None:
                    print("INVALID INDEX")
                    continue
                Connection.cursor.execute(
                    "SELECT COUNT(*) FROM retweets WHERE tid = ?", (tid,))
                retweets_count = Connection.cursor.fetchone()[0]
                Connection.cursor.execute(
                    "SELECT COUNT(*) FROM tweets WHERE replyto = ?", (tid,))
                replies_count = Connection.cursor.fetchone()[0]

                print(
                    f"Tweet [{cmd[1]}] has {retweets_count} retweets and {replies_count} replies")
            else:
                print("INVALID COMMAND -_-")
                continue

    @staticmethod    
    def get_user_info(usr: int, name: str) -> None:
        """Shows the # of tweets, the # of followers, and # of following of a given user

        Args:
            usr (int): the user id of selected user
            name (str): the name of the selected user
        """
        tweets = Search.get_number_of_tweets(usr)
        followers = Search.get_number_of_followers(usr)
        followees = Search.get_number_of_following(usr)

        # prints selected followers details
        print(f"\nYou are looking at {name}'s profile.")
        print(f"Tweet Count: {tweets}\t Followers: {followers} \t Following: {followees}")


    @staticmethod
    def get_number_of_tweets(usr: int) -> int:
        """Gets the # of tweets that a given user has posted

        Args:
            usr (int): user id of the chosen user

        Returns:
            int: # of tweets
        """
        assert Connection.is_connected()
        # number of tweets
        query = "SELECT COUNT(*) FROM tweets WHERE writer = ?"
        Connection.cursor.execute(query, (usr,))
        tweetResult = Connection.cursor.fetchone()

        if tweetResult == None:
            tweetResult[0] = 0
        return tweetResult[0]


    @staticmethod
    def get_number_of_followers(usr: int) -> int:
        """Gets the # of users following a given user

        Args:
            usr (int): user id of the chosen user

        Returns:
            int: # of followers following
        """
        assert Connection.is_connected()
        query = "SELECT COUNT(*) FROM follows WHERE flwee = ?"
        Connection.cursor.execute(query, (usr,))
        result = Connection.cursor.fetchone()
        if result == None:
            return 0
        else:
            return result[0]


    @staticmethod
    def get_number_of_following(usr: int) -> int:
        """Gets the # of users a given user is following

        Args:
            usr (int): user id of the chosen user

        Returns:
            int: # of users being followed
        """
        assert Connection.is_connected()
        query = "SELECT COUNT(*) FROM follows WHERE flwer = ?"
        Connection.cursor.execute(query, (usr,))
        result = Connection.cursor.fetchone()
        if result == None:
            return 0
        else:
            return result[0]


    @staticmethod
    def listnum_to_tid(lst: [dict], option_id: str) -> int:
        """Converts an index in a list of tweets to the tid of the selected tweet

        Args:
            lst (list[dict]): list of tweet objects
            option_id (str): index in the list, as a string

        Returns:
            int: tid of the tweet at index option_id, or None if invalid index
        """
        try:
            index = int(option_id)
            if index > len(lst)+1 or index < 1:
                return None
            return int(lst[index-1]['tid'])
        except:
            return None


    @staticmethod
    def print_items(lst: [dict], num_display: int, offset: int, item_type: str) -> None:
        """Prints a list of tweets or users

        Args:
            lst (list[dict]): the list of tweet/user objects
            num_display (int): # of tweets to display per page
            offset (int): # of tweets to skip
            item_type (str): the type of item being displayed (tweet or user)
        """
        assert Connection.is_connected()
        if len(lst) == 0:
            print("No results found!")
            print()
            return

        print("="*80)
        if item_type == 'tweet':
            for idx, item in enumerate(lst[offset:offset + num_display]):
                # list index
                print(f"{idx+offset+1}]")

                if item['replyto'] is not None:
                    # need to get the usr who wrote the parent
                    parentQuery = """
                            SELECT name, writer, text
                            FROM users u, tweets t
                            WHERE u.usr = t.writer
                                AND t.tid = ?"""
                    Connection.cursor.execute(parentQuery, (item['replyto'],))
                    parentResult = Connection.cursor.fetchone()
                    if parentResult[0] is not None:
                        print(f"\t[Replying to {parentResult[0]} (+{parentResult[1]})]")
                        print(f"\t >> {parentResult[2]}")
                        print()

                # tweet body
                print(f"\t{item['name']} (+{item['writer']})")
                print(f"\t{item['text']}")
                print()

                if item['retweeter'] is not None:
                    # need to get the name of the retweeter
                    rtQuery = """
                            SELECT name, usr
                            FROM users
                            WHERE usr = ?"""
                    Connection.cursor.execute(rtQuery, (item['retweeter'],))
                    rtResult = Connection.cursor.fetchone()
                    if rtResult[0] is not None:
                        print(f"\tRetweeted by {rtResult[0]} (+{rtResult[1]}) on", end=" ")
                else:
                    print("", end="\t")
                print(f"{item['tdate']}")
                print()
                print("="*80)

        elif item_type == 'user':
            for idx, item in enumerate(lst[offset:offset + num_display]):
                # list index
                print(f"{idx+offset+1}]")

                # user info
                print(f"\t{item['name']} (+{item['usr']})")
                print(f"\t{item['city']}")
                print()
                print("="*80)

        print(
            f"Showing page {math.ceil(offset / num_display) + 1} of {max(math.ceil(len(lst)/num_display),1)}")
        print()


def AddTestData():
    insert_query = f"""INSERT INTO Users VALUES 
                    (1, 'password1', 'User1', 'user1@example.com', 'City1', 1.0),
                    (2, 'password2', 'User2', 'user2@example.com', 'City2', 2.0),
                    (3, 'password3', 'User3', 'user3@example.com', 'City3', 3.0),
                    (4, 'password4', 'User4', 'user4@example.com', 'City4', 4.0),
                    (5, 'password5', 'User5', 'user5@example.com', 'City5', 5.0),
                    (6, 'password6', 'User6000', 'user6@example.com', 'City6', 6.0),
                    (7, 'password7', 'User', 'user7@example.com', 'UserCity', 7.0),
                    (8, 'password8', 'Sam1', 'sam1@example.com', 'UserCity1', 8.0),
                    (9, 'password9', 'Sam2', 'sam2@example.com', 'UserCity12', 9.0),
                    (10, 'password10', 'User10', 'user10@example.com', 'UserCity123', 10.0),
                    (11, 'password11', 'User100', 'user11@example.com', 'City', 11.0),
                    (12, 'password12', 'Sam', 'user12@example.com', 'SamCity', 12.0),
                    (13, 'password13', 'Bam', 'user13@example.com', 'BamCity', 13.0),
                    (14, 'password13', 'Ram', 'ram@example.com', 'SamC', 13.0),
                    (15, 'parshvaisacoolguy', 'Ham', 'user13@example.com', 'BamCity', 13.0);"""
    Connection.cursor.executescript(insert_query)

    insert_query = f"""INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES 
                    (1, 1, '2023-01-27', 'This is a #test tweet.', NULL),
                    (2, 2, '2023-02-27', 'This is #another tweet that I am reply to someone else with', NULL),
                    (3, 1, '2023-03-27', 'test of 3', NULL),
                    (4, 1, '2023-04-27', 'test of 3', NULL),
                    (5, 1, '2023-05-27', 'test of 3', NULL),
                    (6, 1, '2023-06-27', 'test of 3', NULL),
                    (7, 1, '2023-07-27', 'test of 3', NULL);"""
    Connection.cursor.executescript(insert_query)

    hashtags_data = [
        ('test',),
        ('another',),
        ('thingy',),
    ]
    Connection.cursor.executemany(
        "INSERT INTO hashtags VALUES (?)", hashtags_data)

    mentions_data = [
        (1, 'test'),
        (1, 'another'),
        (2, 'another'),
        (3, 'another'),
        (4, 'another'),
        (5, 'another'),
        (6, 'another'),
        (7, 'another'),
    ]
    Connection.cursor.executemany(
        "INSERT INTO mentions VALUES (?,?)", mentions_data)
    Connection.connection.commit()


if __name__ == "__main__":
    import os
    path = os.path.dirname(os.path.realpath(__file__)) + "/data.db"
    Connection.connect(path)

    Setup.drop_tables()
    Setup.define_tables()
    # Test.insert_test_data()
    AddTestData()

    Login.userID = 2
    Search.search_for_users()
    # Search.search_for_tweets()

    Connection.close()
