import sys
import time
import os.path
import shutil
import datetime as dt

import requests

TASKS_DIR = os.path.dirname(__file__) + '/tasks'

TODOS_LINK = 'https://json.medrating.org/todos'
USERS_LINK = 'https://json.medrating.org/users'

format_date_now = time.strftime('%d.%m.%Y %H:%M', time.localtime())

try:
    todos_data = requests.get(TODOS_LINK).json()
    users_data = requests.get(USERS_LINK).json()

    os.makedirs(TASKS_DIR, exist_ok=True)

    def get_statistics_tasks(client: int, tasks: list):
        """
        Получаем статистику по задачам пользователя.
        """

        get_total_count = 0

        com_title_list = []
        unf_title_list = []

        data_dict = {}

        for todo in tasks:
            userId = todo.get('userId')
            completed = todo.get('completed')
            title = todo.get('title')

            if userId is not None:
                title = (title[:48] + '...') if len(title) > 48 else title
                if userId == client:
                    get_total_count += 1
                    if completed:
                        com_title_list.append(title)
                    else:
                        unf_title_list.append(title)

        data_dict.update({'unf_title_list': unf_title_list})
        data_dict.update({'com_title_list': com_title_list})
        data_dict.update({'get_total_count': get_total_count})

        return data_dict

    for user in users_data:
        user_id = user.get('id')
        name = user.get('name')
        email = user.get('email')
        username = user.get('username')
        company = user.get('company').get('name')
        data = get_statistics_tasks(client=user_id, tasks=todos_data)
        com_title = "\n".join(data.get("com_title_list"))
        unf_title = "\n".join(data.get("unf_title_list"))
        total_count = data.get("get_total_count")
        com_count = len(data.get("com_title_list"))
        unf_count = len(data.get("unf_title_list"))

        lines = [
            f'Отчёт для {company}.',
            f'\n{name} <{email}> {format_date_now}',
            f'\nВсего задач: {total_count}\n',
            f'\nЗавершённые задачи ({com_count}):',
            f'\n{com_title}\n',
            f'\nОставшиеся задачи ({unf_count}):',
            f'\n{unf_title}'
        ]

        file_path = TASKS_DIR + '/' + username + '.txt'

        if os.path.isfile(file_path):
            old_file = os.path.join(file_path)

            gdt = os.path.getmtime(old_file)
            old_d = dt.datetime.fromtimestamp(gdt).strftime('%Y_%m_%dT%H:%M')
            new_file = os.path.join('tasks', f'old_{username}_{old_d}.txt')

            os.rename(old_file, new_file)

        with open(file_path, "w", encoding='utf-8') as file:

            for line in lines:
                file.write(line)
except Exception as error:
    print('Программа была приостановлена: ', error)
    if os.path.isdir(TASKS_DIR):
        shutil.rmtree(TASKS_DIR)
    sys.exit()
