from announcements.models import Announcement
from businesses.models import Business, BusinessBranch, Follow
from communities.models import Community
from django.core.management.base import BaseCommand
from posts.models import Post

from accounts.models import User


class Command(BaseCommand):
    help = "Seeds the database with demo data for local development."

    def handle(self, *args, **options):
        community, _ = Community.objects.get_or_create(
            name="Kisaasi",
            defaults={"city": "Kampala", "address": "Kisaasi Trading Center"},
        )

        admin_user, _ = User.objects.get_or_create(
            email="admin@demo.com",
            defaults={
                "first_name": "Rita",
                "last_name": "Nakato",
                "role": "community admin",
                "community": community,
                "is_active": True,
            },
        )
        admin_user.set_password("demopass123")
        admin_user.save()
        community.admins.add(admin_user)

        second_admin, _ = User.objects.get_or_create(
            email="admin2@demo.com",
            defaults={
                "first_name": "David",
                "last_name": "Okello",
                "role": "community admin",
                "community": community,
                "is_active": True,
            },
        )
        second_admin.set_password("demopass123")
        second_admin.save()
        community.admins.add(second_admin)

        resident, _ = User.objects.get_or_create(
            email="resident@demo.com",
            defaults={
                "first_name": "Amara",
                "last_name": "Muwonge",
                "role": "resident",
                "community": community,
                "is_active": True,
            },
        )
        resident.set_password("demopass123")
        resident.save()

        owner, _ = User.objects.get_or_create(
            email="owner@demo.com",
            defaults={
                "first_name": "Sunrise",
                "last_name": "Bakery",
                "role": "business owner",
                "community": community,
                "is_active": True,
            },
        )
        owner.set_password("demopass123")
        owner.save()

        business, _ = Business.objects.get_or_create(
            name="Sunrise Bakery",
            defaults={
                "owner": owner,
                "community": community,
                "status": Business.APPROVED,
                "category": Business.FOOD_AND_DINING,
            },
        )

        BusinessBranch.objects.get_or_create(
            business=business,
            community=community,
            defaults={
                "address": "Kisaasi Main Road",
                "city": "Kampala",
                "contact_phone": "0700000000",
                "contact_email": "sunrise@demo.com",
                "status": BusinessBranch.APPROVED,
            },
        )

        for name in ["Kisaasi Hardware", "Heights Pharmacy"]:
            other_business, _ = Business.objects.get_or_create(
                name=name,
                defaults={
                    "owner": owner,
                    "community": community,
                    "status": Business.APPROVED,
                    "category": Business.RETAIL_AND_SHOPPING,
                },
            )
            BusinessBranch.objects.get_or_create(
                business=other_business,
                community=community,
                defaults={
                    "address": "Kisaasi Main Road",
                    "city": "Kampala",
                    "contact_phone": "0700000001",
                    "contact_email": f"{name.lower().replace(' ', '')}@demo.com",
                    "status": BusinessBranch.APPROVED,
                },
            )

        Follow.objects.get_or_create(follower=resident, business=business)

        Post.objects.get_or_create(
            author=resident,
            community=community,
            post_type=Post.USER,
            content="Anyone else notice the streetlight near the community hall is out again?",
        )

        Post.objects.get_or_create(
            author=owner,
            branch=business.branches.first(),
            community=community,
            post_type=Post.BUSINESS,
            content="Fresh batch of cardamom rolls just came out of the oven 🍞",
        )

        announcement, created = Announcement.objects.get_or_create(
            title="Power shut off this week",
            defaults={
                "content": "Power shut off this week from 8am-7pm across Kisaasi, Kyanja.",
                "urgency": Announcement.WARNING,
            },
        )
        if created:
            announcement.communities.add(community)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("  Resident login: resident@demo.com / demopass123")
        self.stdout.write("  Business owner login: owner@demo.com / demopass123")
        self.stdout.write("  Community admin login: admin@demo.com / demopass123")
