from database import User, create_tables


def main():
    create_tables()

    user = User()
    user.insert_user("kafejek@gmail.com", "ratatat21")
    user.insert_user("mac@gmail.com", "ratatat21")

    print(user.get_all_users())
    print(user.get_user_where_email("kafejek@gmail.com"))


if __name__ == "__main__":
    main()
