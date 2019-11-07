from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import User


@receiver(pre_delete, sender=User, dispatch_uid='clear custom_fields')
def log_deleted_question(sender, instance, using, **kwargs):
    """
    When deleting User, also delete it's email
    from CustomFields values field
    """
    for field in instance.site.organization.custom_fields.all():
        field.values.pop(instance.email, None)
        field.save()


@receiver(pre_save, sender=User, dispatch_uid='change_email_cfield')
def edit_custom_fields_remove_duplicate_emails(sender, instance, using, **kwargs):
    """
    When changing email of User,
    change it in CustomFields values field
    """
    if not instance._state.adding:  # check if object exists
        old_email = User.objects.get(pk=instance.pk).email
        if instance.email != old_email:
            for field in instance.site.organization.custom_fields.all():
                field.values.pop(old_email, None)
                field.save()
