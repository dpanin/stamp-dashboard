from sys import argv
from app import db, models

db.create_all()

statuses = ['Заявление зарегистрировано', 'Акцизные марки изготовлены', 'Обязательство принято', 'Обеспечение принято',
            'Марки получены', 'Отчет принят']

for status in statuses:
    db.session.add(models.Status(name=status))

username = argv[1]
email = argv[2]
password = argv[3]
role_id = int(argv[4])

u = models.User(username=username, email=email, password=password, role_id=role_id)
db.session.add(u)
db.session.commit()

print('Done.')
