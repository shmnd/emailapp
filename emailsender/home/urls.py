from django.conf import settings
from django.urls import path, include
from home.views import (
    subscribe_view, tag_create, tag_delete, tag_update, tag_list, template_list,
    template_create, template_update, template_delete, subscriber_list, csv_upload,
    export_subscribers, send_email_view, template_view, track_email_open,
    email_sent_summary, email_sent_summary_download,
    CreateEnquiresApiView,EnquriryListApiView,EmailUnsubscriptionApiView
)

from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static

app_name = 'home'

urlpatterns = [

    # Subscriber    
    path('', login_required(subscribe_view), name='subscribe'),
    path('subscribers/', login_required(subscriber_list), name='subscriber_list'),
    path("csv-upload/", login_required(csv_upload), name="csv_upload"),
    path('subscribers/export/', login_required(export_subscribers), name='export_subscribers'),

    # Tinymce
    path('tinymce/', include('tinymce.urls')),

    # Tag Management URLs
    path('tags/', login_required(tag_list), name='tag_list'),
    path('tags/create/', login_required(tag_create), name='tag_create'),
    path('tags/update/<int:tag_id>/', login_required(tag_update), name='tag_update'),
    path('tags/delete/<int:tag_id>/', login_required(tag_delete), name='tag_delete'),

    # Template Management URLs
    path('templates/', login_required(template_list), name='template_list'),
    path('templates/create/', login_required(template_create), name='template_create'),
    path('templates/update/<int:pk>/', login_required(template_update), name='template_update'),
    path('templates/delete/<int:pk>/', login_required(template_delete), name='template_delete'),
    path('template/view/<int:template_id>/', login_required(template_view), name='template_view'),

    # Send Template
    path("send-email/", login_required(send_email_view), name="send_email"),
    path("email-summary/", login_required(email_sent_summary), name="email_sent_summary"),
    path("email-summary-download/", login_required(email_sent_summary_download), name="email_summary_download"),

    # Tracking Emails
    path('track-email/', login_required(track_email_open), name='track_email_open'),

    # api of enquiries
    path('create-enquiry/',CreateEnquiresApiView.as_view()),
    path('enquiry-list/',EnquriryListApiView.as_view()),
    path('unsubscribe-user/',EmailUnsubscriptionApiView.as_view(),name='unsubscribe-user')

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
