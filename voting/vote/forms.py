from django import forms


class VotingForm(forms.Form):
    question = forms.CharField()
    author = forms.CharField()


from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # do not require password confirmation
        del self.fields['password2']


class AuthForm(forms.Form):
    login = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
