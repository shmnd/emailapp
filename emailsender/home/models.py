from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from django.utils.timezone import now
# Create your models here.


class AbstractDateFieldMix(models.Model):
    created_date              = models.DateTimeField( auto_now_add=True, editable=False, blank=True, null=True)
    modified_date             = models.DateTimeField( auto_now=True, editable=False, blank=True, null=True)

    class Meta:
        abstract = True

class Tags(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

class Subscriber(AbstractDateFieldMix):
    
    email               = models.EmailField(_('Email'),max_length=255,blank=True, null=True,unique=True)
    bounced_email       = models.EmailField(_('Bounced_Email'),max_length=255,blank=True, null=True, unique=True)
    subscribed_email    = models.EmailField(_('Subscribed_Email'),max_length=255,blank=True, null=True, unique=True)
    unsubscribed_email  = models.EmailField(_('Unsubscribed_Email'),max_length=255,blank=True, null=True, unique=True)
    non_subscriber      = models.EmailField(_('Non_Subscriber_Email'),max_length=255,blank=True, null=True, unique=True)
    active_user         = models.BooleanField(default=True)
    tags                = models.ManyToManyField(Tags, blank=True)
    is_active           = models.BooleanField(default=True)

    def __str__(self):
        return self.email or self.subscribed_email or self.bounced_email or self.unsubscribed_email or self.non_subscriber


class Template(AbstractDateFieldMix):
    template_name         = models.CharField(max_length=225,blank=True,null=True,unique=True)
    email_subject         = models.CharField(max_length=255,blank=True, null=True)
    email_body            = HTMLField(blank=True, null=True)
    logo                  = models.ImageField(upload_to="email_logos/", blank=True, null=True, help_text="Company logo for the email")
    button_text           = models.CharField(max_length=50, default="Click Here",blank=True, null=True, help_text="Text displayed on the button")
    button_color          = models.CharField(max_length=7, default="#007BFF",blank=True, null=True,  help_text="Hex color code for the button")
    button_url            = models.URLField(blank=True, null=True, help_text="URL the button redirects to")
    contact_email         = models.EmailField(blank=True, null=True,help_text="Support email address")
    unsubscribe_url       = models.URLField(blank=True, null=True,help_text="Unsubscribe link")
    privacy_policy_url    = models.URLField(blank=True, null=True,help_text="Privacy policy link")
    image                 = models.ImageField(upload_to="email_logos/", blank=True, null=True, help_text="Image for body")
    count                 = models.PositiveIntegerField(blank=True, null=True,default=0) 

    def __str__(self):
        return self.template_name


class EmailSummery(AbstractDateFieldMix):
    sended_emails   = models.EmailField(blank=True, null=True)
    template_names  = models.CharField(max_length=225, blank=True, null=True)
    status          = models.CharField(max_length=50, choices=[('Sent', 'Sent'), ('Failed', 'Failed')], default='Sent')
    failure_reason  = models.TextField(blank=True, null=True)
    subscriber_id   = models.ForeignKey(Subscriber, on_delete=models.SET_NULL, blank=True, null=True)
    template_id     = models.ForeignKey(Template, on_delete=models.SET_NULL, blank=True, null=True)
    opened_at       = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.template_names} - {self.sended_emails} - {self.status}"



class EmailOpenTracking(models.Model):
    email           = models.EmailField(blank=True, null=True)
    subscriber_id   = models.ForeignKey(Subscriber,on_delete=models.CASCADE,blank=True, null=True)
    template_id     = models.ForeignKey(Template,on_delete=models.CASCADE,blank=True, null=True)
    subject         = models.CharField(max_length=255, null=True, blank=True)
    opened_at       = models.DateTimeField(blank=True, null=True,auto_now_add=True)

    class Meta:
        unique_together = ("email", "template_id")  # ✅ Prevent duplicates
