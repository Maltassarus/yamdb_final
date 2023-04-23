from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):

    ROLES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор')
    )

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует',
        },
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField(
        'email адрес',
        max_length=254,
        unique=True,
    )

    role = models.CharField(
        'Роль',
        max_length=15,
        default=ROLES[1],
    )
    bio = models.TextField('О себе', blank=True)

    @property
    def is_admin(self):
        return self.role == self.ROLES[2]

    @property
    def is_moderator(self):
        return self.role == self.ROLES[1]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]
