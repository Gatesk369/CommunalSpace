from django.contrib import admin

from .models import EmailVerificationToken, PasswordResetToken, User

admin.site.register(User)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
