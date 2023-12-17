#!/bin/python3
# main.py

import os
import sys
from Connection import Connection
from Setup import Setup
from Shell import Shell
from Test import Test


def main():
    """Main method. Invoked when the central program is run."""
    # connect to the database
    argc = len(sys.argv)
    if "--db-path" in sys.argv:
        if sys.argv.index("--db-path") == argc-1:
            print("Invalid command-line arguments!")
            os._exit(1)
        dbPath = sys.argv[sys.argv.index("--db-path") + 1]
    else:
        dbPath = os.path.dirname(os.path.realpath(__file__)) + "/data.db"
    Connection.connect(dbPath)

    # provide an option to drop all tables (fresh start)
    if "--reset" in sys.argv or "--test-mode" in sys.argv:
        Setup.drop_tables()

    # define the tables in case they haven't been
    # (does nothing if the tables already exist/have been provided)
    Setup.define_tables()

    # insert mock data for testing
    if "--test-mode" in sys.argv:
        Test.insert_test_data()

    # welcome message, present infinite shell
    Shell.clear()
    print("Welcome to Shell Twitter!")
    print("Type 'help' at any shell prompt (>>>) to see a list of available commands")
    print()
    while True:
        cmd = input(">>> ").strip().lower()
        Shell.main_menu_do(cmd)


if __name__ == "__main__":
    main()
