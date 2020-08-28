import sqlite3

class Sql():
    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file, check_same_thread=False)
        self.cur = self.con.cursor()
    def isgroupregistered(self, group_id):
        return bool(len(self.cur.execute(f"SELECT * FROM groups WHERE `group_id` = {group_id}").fetchall()))
    def create(self, db_name, group_title):
        with self.con:
            try:
                self.cur.execute(f"CREATE TABLE [{db_name}] (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER (11) NOT NULL, first_name VARCHAR (255), last_name VARCHAR (255), status VARCHAR (255) DEFAULT member, messages INTEGER (11) DEFAULT (0), warns INTEGER (11) DEFAULT (0))")
                if not self.isgroupregistered(db_name):
                    self.cur.execute(f"INSERT INTO `groups` (`group_id`, `title`) VALUES ({db_name}, '{group_title}')")
                self.con.commit()
                return True
            except:
                return False

    def private_is_admin(self, user_id, first_name, text=None):
        with self.con:
            groups = self.cur.execute(f"SELECT * FROM `groups`").fetchall()
            for group in groups:
                group_info = self.cur.execute(f"SELECT COUNT(*) FROM [{group[1]}]").fetchall()
                if user_id == self.cur.execute(f"SELECT user_id FROM [{group[1]}]").fetchall()[0][0]:
                    if self.cur.execute(f"SELECT * FROM [{group[1]}] WHERE `user_id` = {user_id}").fetchall()[0][
                        4] == "administrator" or \
                            self.cur.execute(f"SELECT * FROM [{group[1]}] WHERE `user_id` = {user_id}").fetchall()[0][
                                4] == "creator":
                            return groups
                            # return f"Sizning guruhingiz nomi: <i>{groups[0][2]}</i>\nGuruhingiz a'zolari soni: <i>{group_info}ta</i>\nGuruhdagi xabarlar soni: <i>{group_info}</i>"
                else:
                    return f"Salom, {first_name}!\nGuruhni tartiblovchi botga xush kelibsiz.\nBotdan foydalanish uchun yaratuvchiga murojaat qiling ↓↓↓\n\n<b>Developer:</b> @murodov_azizmurod"
    def add_user(self, group_id, user):
        with self.con:
            self.cur.execute(f"INSERT INTO [{group_id}] (`user_id`, `first_name`, `last_name`, `status`) VALUES(?, ?, ?, ?)", user)
            self.con.commit()
    def user(self, group_id, id):
        with self.con:
            self.info = self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (id,)).fetchall()
            self.ishave = bool(len(self.info))
            return {
                "id": self.info[0][0],
                "user_id": self.info[0][1],
                "first_name": self.info[0][2],
                "last_name": self.info[0][3],
                "status": self.info[0][4],
                "messages": self.info[0][5],
                "warnings": self.info[0][6],
                "excist": self.ishave
            }
    def get_user(self, group_id, id):
        with self.con:
            return self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (id,)).fetchall()
    def check_user(self, group_id, id):
        with self.con:
            return bool(len(self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (id,)).fetchall()))
    def get_all_user(self, group_id):
        with self.con:
            return self.cur.execute(f"SELECT * FROM `{group_id}`").fetchall()
    def users_list(self, group_id, limit=None, start=None):
        with self.con:
            list = self.get_all_user(group_id)[start:limit]
            count = len(list)
            text = "Ishtirokchilar:\nNAME - MSG - WARNS\n"
            for i in range(count):
                text = text + f"{list[i][2]} - {list[i][5]} - {list[i][6]}\n"
            return text
    def top_users(self, group_id):
        with self.con:
            users_who_have_messages = self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `messages` >= 1.0 ORDER BY `messages` DESC").fetchall()
            acive_users_count = len(users_who_have_messages)
            if (acive_users_count >= 1):
                text = "Guruhning eng faol ishtirokchilari:\n"
            else:
                text = "Faol ishtirokchilar mavjud emas!"
            for i in range(acive_users_count):
                if (users_who_have_messages[i][4] == "creator" or users_who_have_messages[i][4] == "administrator"):
                    text = text + f"{i+1}. {users_who_have_messages[i][2]} (admin) - {users_who_have_messages[i][5]}\n"
                else:
                    text = text + f"{i + 1}. {users_who_have_messages[i][2]} - {users_who_have_messages[i][5]}\n"
            return text
    def iswarned(self, group_id, id):
        with self.con:
            return bool(len(self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `warns` >= 1.0 AND `user_id` = ?", (id,)).fetchall()))
    def give_warn(self, group_id, id):
        with self.con:
            self.cur.execute(f"UPDATE `{group_id}` SET `warns` = `warns` + 1 WHERE `user_id` = ?", (id,))
            self.con.commit()
    def give_message(self, group_id, id, messages_count):
        with self.con:
            self.cur.execute(f"UPDATE `{group_id}` SET `messages` = `messages` + 1 WHERE `user_id` = ?", (id,))
            self.cur.execute(f"UPDATE `groups` SET `total_messages` = {messages_count} WHERE `group_id` = ?", (group_id,))
            self.con.commit()


    # def add(self, group_id, user_id, first_name, last_name, status):
    #     with self.con:
    #         user = (
    #             user_id,
    #             first_name,
    #             last_name,
    #             status
    #         )
    #         self.cur.execute(f"INSERT INTO [{group_id}] (`user_id`, `first_name`, `last_name`, `status`) VALUES(?, ?, ?, ?)", user)
    #         self.con.commit()
    #
    # def user(self, group_id, id):
    #     with self.con:
    #         self.info = self.cur.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (id,)).fetchall()
    #         self.ishave = bool(len(self.info))
    #         return {
    #             "id": self.info[0][0],
    #             "user_id": self.info[0][1],
    #             "first_name": self.info[0][2],
    #             "last_name": self.info[0][3],
    #             "status": self.info[0][4],
    #             "messages": self.info[0][5],
    #             "warnings": self.info[0][6],
    #             "excist": self.ishave
    #         }
