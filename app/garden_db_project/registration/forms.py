# app/garden_db_project/registration/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Consider adding password validation if needed:
# from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class FirstAdminRegistrationForm(forms.Form):
    """
    A form for creating the first admin user.
    Includes basic validation and password confirmation.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}) # Add bootstrap class
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=_("Enter a secure password."),
        required=True
    )
    password_confirm = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=_("Enter the same password as before, for verification."),
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Use Django's built-in validator logic if possible, or replicate essential checks
        # For simplicity here, just check existence. Production might need more.
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                _("A user with that username already exists."),
                code='username_exists',
            )
        # You might want to add more validation here based on User model constraints
        # For example, check allowed characters if not using default User model validators
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', ValidationError(
                    _("The two password fields didn't match."),
                    code='password_mismatch',
                ))
            # Optionally add password strength validation here
            # try:
            #     validate_password(password, user=None) # Pass user=None for creation
            # except ValidationError as e:
            #     self.add_error('password', e)

        return cleaned_data

    def save(self):
        """
        Creates the superuser. Assumes form is valid.
        """
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        # Use create_user to handle username normalization etc.
        user = User.objects.create_user(username=username, password=None) # Create without password initially
        user.set_password(password) # Set password securely
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
