import os
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Create the default admin account from environment variables (idempotent)'

    def handle(self, *args, **kwargs):
        email = os.environ.get('ADMIN_EMAIL', 'admin@escrs.ac.uk')
        password = os.environ.get('ADMIN_PASSWORD', 'Admin@ESCRS2025')
        full_name = os.environ.get('ADMIN_NAME', 'System Admin')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.role != 'admin':
                user.role = 'admin'
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['role', 'is_staff', 'is_superuser'])
                self.stdout.write(self.style.SUCCESS(f'Promoted {email} to admin'))
            else:
                self.stdout.write(f'Admin {email} already exists — skipping')
        else:
            User.objects.create_superuser(email=email, password=password, full_name=full_name)
            self.stdout.write(self.style.SUCCESS(f'Admin account created: {email}'))
