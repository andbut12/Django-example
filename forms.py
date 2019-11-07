import ast

from dateutil.parser import parse

from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _

from user.models import User
from user.utils import get_choices


class UserFormCreate(forms.ModelForm):
    """
    Creates user from email and password
    """
    error_messages = {
        'duplicate_email': _('A user with that email already exists.'),
        'password_mismatch': _('The two password fields didn\'t match.'),
    }
    email = forms.CharField(label=_('Email'), max_length=30)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']


class UserFormChange(UserChangeForm):
    def __init__(self, *args, **kwargs):
        """
        It's overrided because we need prettified
        representation of CustomFields in UserAdmin
        """
        super(UserFormChange, self).__init__(*args, **kwargs)
        self.custom_fields_qs = self.instance.site.organization.custom_fields.all()

        for field in self.custom_fields_qs:
            field_name, initial = field.name, field.values.get(self.instance.email)
            field_type, required = field.field_type, field.required
            # These constants are different, because we need an empty choice for DropDown
            CHOICES = get_choices(field)
            DROP_CHOICES = get_choices(field, dropdown=True)

            if field_type == 1:  # Checkbox. We need choices here, so that 'False' value could also be stored in table
                self.fields[field_name] = forms.CharField(widget=forms.Select(choices=[(True, 'Да'), (False, 'Нет')]),
                                                          required=required, initial=ast.literal_eval(initial))
            elif field_type == 2:  # Text
                self.fields[field_name] = forms.CharField(widget=forms.TextInput(), required=required, initial=initial)
            elif field_type == 3:  # TextArea
                self.fields[field_name] = forms.CharField(widget=forms.Textarea(), required=required, initial=initial)
            elif field_type == 4:  # DropDown menu
                self.fields[field_name] = forms.CharField(widget=forms.Select(choices=DROP_CHOICES),
                                                          required=required, initial=initial)
            elif field_type == 5:  # MultipleChoice
                self.fields[field_name] = forms.MultipleChoiceField(choices=CHOICES, required=required, initial=initial)

            elif field_type == 6:  # Date
                if initial:
                    initial = parse(initial)
                self.fields[field_name] = forms.DateField(widget=widgets.AdminDateWidget(),
                                                          required=required, initial=initial)
            elif field_type == 7:  # DateTime
                if initial:
                    initial = parse(initial)
                self.fields[field_name] = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(),
                                                                   required=required, initial=initial)

    def save(self, commit=False):
        instance = super(UserFormChange, self).save(commit=False)
        for field in self.custom_fields_qs:
            if self.cleaned_data[field.name]:
                field.values.update({instance.email: str(self.cleaned_data[field.name])})
            else:
                field.values.pop(instance.email, '')  # If we removed field value, remove it from CustomField's values
            field.save()
        return instance
