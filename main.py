from database import User, create_tables


def main():
    # create_tables()
    User.create_table()

    user = User()
    user.insert_user("kafejek@gmail.com", "ratatat21")

    print(user.get_all_users())


if __name__ == "__main__":
    main()
