from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from home.models import Subscriber,Tags,Template
from tinymce.widgets import TinyMCE

class TagForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ["name"]

class TemplateForm(forms.ModelForm):
    email_body = forms.CharField(widget=TinyMCE(attrs={'cols':80,'rows':20}))
    button_color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'style': 'width: 80px; height: 40px;'}),
        required=False
    )
    class Meta:
        model = Template
        fields = [
            'template_name',
            'email_subject',
            'email_body',
            'logo',
            'image',
            'button_text',
            'button_color',
            'button_url',
            'contact_email',
            'unsubscribe_url',
            'privacy_policy_url',
            
        ]
        widgets = {
            'button_color': forms.TextInput(attrs={'type': 'color'}),  # Color picker for button color
        }


    
class SubscribeForm(forms.Form):
    email = forms.EmailField()
    tags = forms.ModelChoiceField(
        queryset= Tags.objects.all(),
        required=False
    )

    VALID_EMAIL_EXTENSIONS = [".com"]  

    def clean_email(self):
        emails = self.cleaned_data.get('email')
        emails = emails.lower().strip()

        try:
            validate_email(emails)
            username, domain = emails.split("@")
        except ValueError:
            raise forms.ValidationError("Invalid email address format.")
        
        if not any(domain.endswith(ext) for ext in self.VALID_EMAIL_EXTENSIONS):
            raise forms.ValidationError("Invalid email domain!")
        
        return emails
    

            
