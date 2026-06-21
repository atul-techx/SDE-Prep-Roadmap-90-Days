from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    contact_number = forms.CharField(max_length=20, required=True, label="Mobile Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        # Allow optional + at the start
        clean_num = contact_number.lstrip('+')
        if not clean_num.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(clean_num) < 10:
            raise forms.ValidationError("Mobile number must be at least 10 digits.")
        return contact_number
