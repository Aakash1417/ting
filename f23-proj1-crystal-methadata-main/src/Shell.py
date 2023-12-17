import os
from Connection import Connection
from Login import Login
from Feed import Feed
from Search import Search
from ComposeTweet import ComposeTweet


class Shell:
    @staticmethod
    def clear():
        """Clears the screen"""
        if os.name == 'posix':
            os.system('clear')
        elif os.name == 'nt':
            os.system('cls')


    @staticmethod
    def get_main_options() -> [str]:
        """Gets a list of the keywords globally available at all times

        Returns:
            list[str]: list of global keywords
        """
        options = []
        if Login.userID is None:
            options.append("login")
            options.append("register")
        else:
            options.append("feed")
            options.append("searchtweets")
            options.append("compose")
            options.append("searchusers")
            options.append("followers")
            options.append("logout")
        options.append("help")
        options.append("clear")
        options.append("exit")
        return options


    @staticmethod
    def main_menu_do(cmd: str, additional_options: [str] = []) -> None:
        """Central controller that executes actions based on the command provided.
            Routes actions such as login, registration, displaying feed, searching, etc.

        Args:
            cmd (str): the global command to execute.
            additional_options (list[str], optional): Additional context-dependent
                keywords to print in help text. Defaults to [].
        """
        options = Shell.get_main_options()
        if cmd in options:
            if cmd == "login":
                if Login.login():
                    Feed.show_feed()
            elif cmd == "register":
                Login.register()
            elif cmd == "feed":
                Feed.show_feed()
            elif cmd == "searchtweets":
                Search.search_for_tweets()
            elif cmd == "compose":
                ComposeTweet.createTweet()
            elif cmd == "searchusers":
                Search.search_for_users()
            elif cmd == "followers":
                Search.search_for_followers()
            elif cmd == "logout":
                Login.logout()
            elif cmd == "help":
                Shell.print_menu(additional_options)
            elif cmd == "exit":
                print("Closing Program :(")
                Connection.close()
                os._exit(0)
            elif cmd == "clear":
                Shell.clear()
        else:
            print("INVALID COMMAND -_-")


    @staticmethod
    def print_menu(additional_options: [str] = []) -> None:
        """Prints the help menu of all the currently-available keywords

        Args:
            additional_options (list[str], optional): Additional context-dependent
                keywords to print in help text. Defaults to [].
        """
        options = Shell.get_main_options()
        options = options[:-3] + additional_options + options[-3:]

        print("="*80)
        print()
        for option in options:
            print(f"- {option.capitalize()}")
        print()
        print("="*80)
