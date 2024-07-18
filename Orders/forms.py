from django import forms
from phonenumber_field.formfields import PhoneNumberField




class CheckOutForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'})
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'})
    )
    phone = PhoneNumberField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'})
    )