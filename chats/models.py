from django.db import models

from django.utils.translation import gettext_lazy as _


class Chat(models.Model):
    SIMPLE_USER = "user"
    PLUMBER = "plumber"
    ADMIN = "admin"
    USER_TYPES = (
        (SIMPLE_USER, _("User")),
        (PLUMBER, _("Plumber")),
        (ADMIN, _("Admin")),
    )

    UZBEK = "uzbek"
    RUSSIAN = "russian"
    LANGUAGES = (
        (UZBEK, "Uzbek"),
        (RUSSIAN, "Russian"),
    )
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    chat_id = models.IntegerField()
    user_type = models.CharField(max_length=32, choices=USER_TYPES, null=True, blank=True)
    language = models.CharField(max_length=15, choices=LANGUAGES, null=True, blank=True)
    is_joined_channels = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name if self.first_name else f"Chat object ({self.id})"
