from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model.
    """
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['username']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_name_email'
            ),
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """
    Subscription model.
    """

    user = models.ForeignKey(
        CustomUser,
        verbose_name=_('subscriber'),
        related_name='subscriber',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name=_('recipe author'),
        related_name='subscribed',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['author']
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_author_not_self'
            ),
        ]

    def __str__(self):
        return (
            self.user.get_username()
            + ' subscribe '
            + self.author.get_username()
        )
