from django.db import models


class Announcement(models.Model):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    district = models.ForeignKey("common.District", on_delete=models.CASCADE, null=True, blank=True)
    location = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to="announcements/", null=True, blank=True)
    chat = models.ForeignKey("chats.Chat", on_delete=models.CASCADE)
    additional_info = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.fullname if self.fullname else f"Chat object {self.id}"
