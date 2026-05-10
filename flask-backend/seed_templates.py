"""
Seed starter templates for the website builder.
Creates a library of professionally designed Bootstrap starter templates.
Run: python seed_templates.py
"""
import json
import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.database import db
from app.models.template import Template


# Starter template definitions
STARTER_TEMPLATES = [
    {
        'name': 'landing-simple',
        'display_name': 'Simple Landing Page',
        'description': 'A clean, modern landing page with hero section, features, pricing, and contact form. Perfect for SaaS products or apps.',
        'category': 'landing',
        'is_premium': False,
        'is_public': True,
        'tags': ['landing', 'saas', 'hero', 'features', 'pricing'],
        'thumbnail_url': None,
        'content': {
            'theme': 'default',
            'pages': [
                {
                    'title': 'Home',
                    'slug': 'home',
                    'content': '',
                    'tree': {
                        'type': 'Navbar',
                        'props': {
                            'brand': 'Your Brand',
                            'bg': 'bg-light',
                            'expand': 'lg',
                        },
                        'children': []
                    }
                }
            ]
        }
    },
    {
        'name': 'landing-modern',
        'display_name': 'Modern Landing Page',
        'description': 'A bold, contemporary landing page with Gradient hero, testimonials, and CTA sections. Great for startups.',
        'category': 'landing',
        'is_premium': True,
        'is_public': True,
        'tags': ['landing', 'startup', 'gradient', 'hero'],
        'thumbnail_url': None,
        'content': {
            'theme': 'cosmo',
            'pages': []
        }
    },
    {
        'name': 'portfolio-creative',
        'display_name': 'Creative Portfolio',
        'description': 'Showcase your work with this elegant portfolio template. Includes project gallery, about section, and contact form.',
        'category': 'portfolio',
        'is_premium': False,
        'is_public': True,
        'tags': ['portfolio', 'creative', 'gallery', 'about'],
        'thumbnail_url': None,
        'content': {
            'theme': 'journal',
            'pages': []
        }
    },
    {
        'name': 'blog-clean',
        'display_name': 'Clean Blog Template',
        'description': 'A minimalist blog template with article cards, sidebar, and clean typography. Perfect for personal or tech blogs.',
        'category': 'blog',
        'is_premium': False,
        'is_public': True,
        'tags': ['blog', 'clean', 'minimal', 'article'],
        'thumbnail_url': None,
        'content': {
            'theme': 'lumen',
            'pages': []
        }
    },
    {
        'name': 'business-corporate',
        'display_name': 'Corporate Business',
        'description': 'Professional corporate website template with services, team, testimonials, and contact sections.',
        'category': 'business',
        'is_premium': False,
        'is_public': True,
        'tags': ['business', 'corporate', 'services', 'team'],
        'thumbnail_url': None,
        'content': {
            'theme': 'spacelab',
            'pages': []
        }
    },
    {
        'name': 'restaurant-food',
        'display_name': 'Restaurant & Food',
        'description': 'Beautiful restaurant template with menu, reservations, and gallery sections.',
        'category': 'restaurant',
        'is_premium': False,
        'is_public': True,
        'tags': ['restaurant', 'food', 'menu', 'reservation'],
        'thumbnail_url': None,
        'content': {
            'theme': 'sandstone',
            'pages': []
        }
    },
    {
        'name': 'ecommerce-shop',
        'display_name': 'E-commerce Shop',
        'description': 'A sleek e-commerce template with product grid, cart preview, and checkout flow.',
        'category': 'ecommerce',
        'is_premium': True,
        'is_public': True,
        'tags': ['ecommerce', 'shop', 'product', 'cart'],
        'thumbnail_url': None,
        'content': {
            'theme': 'united',
            'pages': []
        }
    },
    {
        'name': 'resume-professional',
        'display_name': 'Professional Resume',
        'description': 'Clean and professional online resume/CV template for job seekers and freelancers.',
        'category': 'resume',
        'is_premium': False,
        'is_public': True,
        'tags': ['resume', 'cv', 'professional', 'portfolio'],
        'thumbnail_url': None,
        'content': {
            'theme': 'yeti',
            'pages': []
        }
    },
    {
        'name': 'event-conference',
        'display_name': 'Conference Event',
        'description': 'Modern event website for conferences, meetups, and workshops with schedule and speakers.',
        'category': 'event',
        'is_premium': False,
        'is_public': True,
        'tags': ['event', 'conference', 'schedule', 'speakers'],
        'thumbnail_url': None,
        'content': {
            'theme': 'superhero',
            'pages': []
        }
    },
    {
        'name': 'nonprofit-organization',
        'display_name': 'Non-profit Organization',
        'description': 'Warm and trustworthy template for non-profits, charities, and community organizations.',
        'category': 'nonprofit',
        'is_premium': False,
        'is_public': True,
        'tags': ['nonprofit', 'charity', 'donation', 'community'],
        'thumbnail_url': None,
        'content': {
            'theme': 'minty',
            'pages': []
        }
    },
    {
        'name': 'coming-soon',
        'display_name': 'Coming Soon',
        'description': 'Simple countdown and email capture page for websites under development.',
        'category': 'coming-soon',
        'is_premium': False,
        'is_public': True,
        'tags': ['coming-soon', 'countdown', 'launch'],
        'thumbnail_url': None,
        'content': {
            'theme': 'default',
            'pages': []
        }
    },
]


def seed_templates():
    """Seed starter templates into the database."""
    app = create_app('development')
    with app.app_context():
        created_count = 0
        updated_count = 0

        for template_data in STARTER_TEMPLATES:
            name = template_data['name']

            # Check if template exists
            existing = Template.find_by_name(name)

            if existing:
                # Update existing
                existing.update(
                    display_name=template_data['display_name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    is_premium=template_data['is_premium'],
                    is_public=template_data['is_public'],
                    tags=json.dumps(template_data['tags']),
                    thumbnail_url=template_data['thumbnail_url'],
                    content=json.dumps(template_data['content']),
                )
                updated_count += 1
                print(f"✓ Updated: {template_data['display_name']}")
            else:
                # Create new
                template = Template(
                    name=name,
                    display_name=template_data['display_name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    is_premium=template_data['is_premium'],
                    is_public=template_data['is_public'],
                    tags=json.dumps(template_data['tags']),
                    thumbnail_url=template_data['thumbnail_url'],
                    content=json.dumps(template_data['content']),
                )
                from app.database import db
                db.session.add(template)
                created_count += 1
                print(f"+ Created: {template_data['display_name']}")

        db.session.commit()

        print(f"\n{'='*60}")
        print(f"Seeding complete!")
        print(f"  Created: {created_count} templates")
        print(f"  Updated: {updated_count} templates")
        print(f"{'='*60}")

        # Show summary
        all_templates = Template.find_all(page=1, limit=1000)[0]
        print(f"\nTotal templates in database: {len(all_templates)}")
        categories = Template.get_categories()
        print(f"Categories: {', '.join(categories)}")


if __name__ == '__main__':
    seed_templates()