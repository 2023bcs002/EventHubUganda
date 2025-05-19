from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='First Name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your first name',
                'class': 'form-control'
            }
        )
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Last Name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter your last name',
                'class': 'form-control'
            }
        )
    )
    email = forms.EmailField(
        max_length=254,
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Enter your email address',
                'class': 'form-control'
            }
        )
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Choose a username',
                'class': 'form-control'
            }
        )
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter your password',
                'class': 'form-control'
            }
        )
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm your password',
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user 