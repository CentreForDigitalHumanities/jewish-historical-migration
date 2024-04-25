from django.core.management import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

import data.models as models


class Command(BaseCommand):
    help = "Create or retrieve an API authentication token for a given user. Create the user if it does not yet exist."

    def add_arguments(self, parser):
        parser.add_argument('username', help='The username to get a token for')
    
    def handle(self, username: str, **options):
        # Get user, or create if does not yet exist
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username)
            self.stdout.write(self.style.SUCCESS(f"Created user {username}."))

        # Get token
        token, created = Token.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created token for user {username}: {token.key}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Retrieved token for user {username}: {token.key}"))
