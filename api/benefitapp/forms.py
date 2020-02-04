from django import forms
from benefitapp.models import Users,Profiles,Followings,Category,Profilecategory,userSocailProfile


my_default_errors = {
    'required': 'Please Enter title.'  
}
class UserForm(forms.ModelForm):    
    class Meta:
        model = Users
        fields = ('email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profiles
        fields = ('firstname', 'lastname')


class UserForm1(forms.Form):
    email = forms.CharField(max_length=256,error_messages=my_default_errors)
    password = forms.CharField(widget=forms.PasswordInput())
	