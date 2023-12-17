from getpass import getpass
from Connection import Connection


class Login:
    userID = None
    name = None

    @staticmethod
    def get_highest_uid() -> int:
        """Finds the id of the user with the highest id

        Returns:
            int: highest user id in the db
        """
        assert Connection.is_connected()
        Connection.cursor.execute("SELECT MAX(usr) FROM users;")
        result = Connection.cursor.fetchone()
        if result[0] is None:
            return 0
        return int(result[0])


    @staticmethod
    def login() -> bool:
        """Runs the login prompt until user authenticates or cancels

        Returns:
            bool: True on successful login, False on cancel
        """
        while (True):
            user = input("\nUser ID (or 'cancel'): ").strip()
            if user.lower() == "cancel":
                print("Login cancelled.\n")
                return False

            if not user.isnumeric():
                print("User ID must be numeric.")
                continue

            uid = int(user)
            pswd = getpass("Password: ")
            if Login.authenticate_user(uid, pswd):
                Login.userID = uid
                return True
            else:
                print("Login credentials do not match. Please try again.")


    @staticmethod
    def authenticate_user(userid: int, password: str) -> bool:
        """Authenticates a user's login credentials

        Args:
            userid (int): id of the user attempting to login
            password (str): attempted password (unhashed)

        Returns:
            bool: True if the user login credentials are valid
        """
        assert Connection.is_connected()

        # check if the user exists
        Connection.cursor.execute(
            "SELECT pwd, name FROM users WHERE usr = :userid;",
            {"userid": userid}
        )
        result = Connection.cursor.fetchone()
        if result is None:
            # no such user exists
            return False

        # otherwise, the query returned a result and the user exists
        # the correct password is the first attribute (index 0)
        correctPswd = result[0]
        if password != correctPswd:
            # password incorrect
            return False
        else:
            # authentication successful
            Login.name = result[1]
            print(f"Welcome back, {Login.name}.")
            print("Here is your feed:\n")
            return True


    @staticmethod
    def register() -> bool:
        """Prompts user for information, then creates a new user in the db

        Returns:
            bool: True on successful registration, False on cancel
        """
        assert Connection.is_connected()

        print("\nCreating new account.")
        print("You will be asked for a name, email, city, timezone, and password, " +
              "after which you can confirm/cancel your registration.\n")
        while (True):
            name = input("Display Name: ").strip()
            email = input("Email Address: ").strip()
            city = input("City: ").strip()
            timezone = input("Timezone (eg. -5): ").strip()
            password = getpass("Password: ")
            cPassword = getpass("Confirm Password: ")

            # pre-creation basic validation
            if '@' not in email or '.' not in email:  # very basic email validation
                print("\nEmail was an invalid format. Please try again.")
                continue
            try:
                timezone = float(timezone)
            except ValueError:
                print("\nTimezone must be a number. Please try again.")
                continue
            if password != cPassword:
                print("\nPasswords entered do not match. Please try again.")
                continue

            # confirm creation before committing
            confirmReg = input(f"\nCreate new account for {name}? (Y/n) ").strip()
            if not confirmReg.lower().startswith('y'):
                print("\nNew user registration cancelled.\n")
                return False

            # create a new user with a unique uid
            uid = Login.get_highest_uid() + 1
            Connection.cursor.execute("""
            INSERT INTO users(usr, pwd, name, email, city, timezone) VALUES
                    (:usr, :pwd, :name, :email, :city, :timezone);
            """, {
                "usr": uid,
                "pwd": password,
                "name": name,
                "email": email,
                "city": city,
                "timezone": timezone
            })
            Connection.connection.commit()
            print(f"\nWelcome, {name}.")
            print(f"Your new user ID is {uid}. You will need this ID later to log in.\n")
            Login.userID = uid
            return True


    def logout() -> None:
        """Logs out any currently logged in user"""
        assert Connection.is_connected()
        assert Login.userID is not None
        print(f"{Login.name}, you have now logged out.\n")
        Login.userID = None
        Login.name = None
