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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'e.g. atul@example.com'})
        self.fields['full_name'].widget.attrs.update({'placeholder': 'e.g. Atul Sharma'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'e.g. 9876543210'})
        
        # UserCreationForm adds password fields usually named 'password' or 'new_password1' etc.
        # We can dynamically add placeholders to any password fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({'placeholder': 'Enter your password'})

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        # Allow optional + at the start
        clean_num = contact_number.lstrip('+')
        if not clean_num.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(clean_num) < 10:
            raise forms.ValidationError("Mobile number must be at least 10 digits.")
        return contact_number
