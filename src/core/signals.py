from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.models import Guest, Assignee


@receiver(post_delete, sender=Guest)
def delete_assignees(sender, instance, **kwargs):
    Assignee.objects.filter(board_id=instance.board_id, user_id=instance.user_id).delete()