"""Core system-page registry for the Website Builder / CMS.

The builder's "Editable Pages" grid used to only show pages someone created
by hand. This module **auto-registers the existing system routes** — the
landing page, Study Corner, Pharmacy, Global News and Clubs — as
``EditablePage`` rows (keyed by the new ``system_key`` field) and seeds each
one with its extracted feature blocks, so admins can edit those sections from
the Block Manager and have the edits render live on the public route.

Behaviour contract (all idempotent):

* ``register_system_pages()`` may be called any number of times — pages and
  blocks are ``get_or_create``-keyed on stable natural keys, so re-runs never
  duplicate rows.
* Admin edits are never clobbered: block content / visibility / order are
  written only when the block is first created. Re-runs only ensure the row
  exists.
* Seeded blocks start ``visible=False`` so the public route keeps rendering
  its default template until an admin edits a section and reveals it from the
  Block Manager.
* The three starter blueprints (PageTemplate) are seeded if missing.
"""

from core.models import ContentBlock, EditablePage, PageTemplate

# system_key → the canonical system page. ``view_name`` is the URL name used
# by the ``cms_system_blocks`` context processor to map a request to its page.
SYSTEM_PAGES = [
    {
        'key': 'home',
        'title': 'Home (Landing Page)',
        'slug': 'home',
        'route_url': '/',
        'view_name': 'home',
        'blocks': [
            {
                'element_id': 'hero-banner',
                'block_type': 'hero',
                'content_json': {
                    'headline': 'Welcome to CampusDash',
                    'subheadline': 'Public University Information & Medical Services System',
                    'image_url': '',
                    'primary_label': 'Login to Dashboard',
                    'primary_url': '/dashboard/',
                },
            },
            {
                'element_id': 'quick-announcements',
                'block_type': 'announcements',
                'content_json': {
                    'title': 'Quick Announcements',
                    'subtitle': 'Latest campus notices at a glance',
                    'items': [
                        {'title': 'Midterm schedule published', 'text': 'See the academic calendar for dates.'},
                        {'title': 'Medical camp this Friday', 'text': 'Free check-ups at the medical center.'},
                    ],
                },
            },
            {
                'element_id': 'feature-grid',
                'block_type': 'features',
                'content_json': {
                    'title': 'Why CampusDash',
                    'subtitle': 'Everything your campus needs in one portal',
                    'items': [
                        {'icon': 'fa-book-open', 'title': 'Study Corner', 'text': 'Notes, lectures and an AI study assistant.'},
                        {'icon': 'fa-prescription-bottle-medical', 'title': 'Online Pharmacy', 'text': 'Order medicines with prescription verification.'},
                        {'icon': 'fa-newspaper', 'title': 'Global News', 'text': 'Live headlines and video news.'},
                    ],
                },
            },
        ],
    },
    {
        'key': 'study-corner',
        'title': 'Study Corner',
        'slug': 'study-corner',
        'route_url': '/study-corner/',
        'view_name': 'study_corner',
        'blocks': [
            {
                'element_id': 'notes-listing',
                'block_type': 'notes',
                'content_json': {
                    'title': 'Academic Notes & Resources',
                    'subtitle': 'Browse lecture materials by department',
                    'items': [
                        {'title': 'Circuit Analysis Lecture Notes', 'course': 'EEE-2101', 'url': '/study-corner/'},
                        {'title': 'C Programming Slides', 'course': 'CSE-1101', 'url': '/study-corner/'},
                    ],
                },
            },
            {
                'element_id': 'youtube-section',
                'block_type': 'youtube',
                'content_json': {
                    'title': 'Video Tutorials & Lectures',
                    'subtitle': 'Search and play lecture videos inline',
                    'placeholder': 'e.g. Circuit Analysis',
                    'embed_url': '',
                },
            },
            {
                'element_id': 'study-assistant',
                'block_type': 'chat',
                'content_json': {
                    'title': 'Study Assistant',
                    'subtitle': 'Ask questions about your courses',
                    'placeholder': 'Type a question and press Enter…',
                },
            },
        ],
    },
    {
        'key': 'pharmacy',
        'title': 'Online Pharmacy & Medical Hub',
        'slug': 'pharmacy',
        'route_url': '/pharmacy/',
        'view_name': 'pharmacy_store',
        'blocks': [
            {
                'element_id': 'category-nav',
                'block_type': 'category_nav',
                'content_json': {
                    'title': 'Shop by Category',
                    'items': [
                        {'label': 'Tablets', 'icon': 'fa-tablets', 'url': '/pharmacy/'},
                        {'label': 'Capsules', 'icon': 'fa-capsules', 'url': '/pharmacy/'},
                        {'label': 'Syrups', 'icon': 'fa-prescription-bottle', 'url': '/pharmacy/'},
                        {'label': 'First Aid', 'icon': 'fa-kit-medical', 'url': '/pharmacy/'},
                    ],
                },
            },
            {
                'element_id': 'hero-promo',
                'block_type': 'promo',
                'content_json': {
                    'headline': 'Medicines delivered to your hall',
                    'subtext': 'Upload a prescription, pay with bKash / Nagad / SSLCommerz, and track your order.',
                    'image_url': '',
                    'primary_label': 'Browse Medicines',
                    'primary_url': '/pharmacy/',
                },
            },
            {
                'element_id': 'top-brands',
                'block_type': 'brands',
                'content_json': {
                    'title': 'Top Brands',
                    'subtitle': 'Trusted medicines in stock',
                    'items': [
                        {'name': 'Square', 'tagline': 'Pharmaceuticals', 'logo_url': ''},
                        {'name': 'Beximco', 'tagline': 'Pharmaceuticals', 'logo_url': ''},
                        {'name': 'ACI', 'tagline': 'Health care', 'logo_url': ''},
                    ],
                },
            },
            {
                'element_id': 'product-grid',
                'block_type': 'products',
                'content_json': {
                    'title': 'Featured Medicines',
                    'subtitle': 'Popular picks from the campus pharmacy',
                    'items': [
                        {'name': 'Napa 500mg', 'price': '৳10', 'url': '/pharmacy/'},
                        {'name': 'Ace 500mg', 'price': '৳8', 'url': '/pharmacy/'},
                        {'name': 'Oradin Syrup', 'price': '৳95', 'url': '/pharmacy/'},
                    ],
                },
            },
        ],
    },
    {
        'key': 'news',
        'title': 'Global News',
        'slug': 'news',
        'route_url': '/news/',
        'view_name': 'news',
        'blocks': [
            {
                'element_id': 'news-search',
                'block_type': 'news_search',
                'content_json': {
                    'title': 'Search the News',
                    'placeholder': 'e.g. bangladesh',
                },
            },
            {
                'element_id': 'image-card-grid',
                'block_type': 'card_grid',
                'content_json': {
                    'title': 'Latest Stories',
                    'subtitle': 'Headlines from around the world',
                    'items': [
                        {'image_url': '', 'title': 'Headline one', 'source': 'Sample Wire', 'url': ''},
                        {'image_url': '', 'title': 'Headline two', 'source': 'Sample Wire', 'url': ''},
                    ],
                },
            },
            {
                'element_id': 'video-feed',
                'block_type': 'video_feed',
                'content_json': {
                    'title': 'Video News',
                    'items': [
                        {'video_id': '', 'title': 'Video headline', 'channel': 'News channel'},
                    ],
                },
            },
        ],
    },
    {
        'key': 'clubs',
        'title': 'Clubs Hub',
        'slug': 'clubs',
        'route_url': '/clubs/',
        'view_name': 'clubs_dashboard',
        'blocks': [
            {
                'element_id': 'clubs-promo',
                'block_type': 'promo',
                'content_json': {
                    'headline': 'Join a campus club',
                    'subtext': 'Explore societies, events and membership.',
                    'image_url': '',
                    'primary_label': 'Explore Clubs',
                    'primary_url': '/clubs/',
                },
            },
        ],
    },
]

# Starter blueprints offered on the builder dashboard for 1-click creation.
BLUEPRINT_TEMPLATES = [
    {
        'name': 'Standard Landing Page',
        'description': 'Hero banner, feature grid and a call-to-action — the classic marketing layout.',
        'layout_json': {
            'sections': [
                {'name': 'hero', 'label': 'Hero Banner'},
                {'name': 'body', 'label': 'Main Content'},
            ],
            'blocks': [
                {'element_id': 'hero-banner', 'section': 'hero', 'type': 'hero'},
                {'element_id': 'feature-grid', 'section': 'body', 'type': 'features'},
                {'element_id': 'cta-banner', 'section': 'body', 'type': 'cta'},
            ],
        },
    },
    {
        'name': 'Resource Hub',
        'description': 'Links, notes listings and a study-assistant prompt for resource-style pages.',
        'layout_json': {
            'sections': [
                {'name': 'hero', 'label': 'Hero Banner'},
                {'name': 'resources', 'label': 'Resources'},
            ],
            'blocks': [
                {'element_id': 'hub-hero', 'section': 'hero', 'type': 'hero'},
                {'element_id': 'quick-links', 'section': 'resources', 'type': 'links'},
                {'element_id': 'notes-list', 'section': 'resources', 'type': 'notes'},
                {'element_id': 'assistant', 'section': 'resources', 'type': 'chat'},
            ],
        },
    },
    {
        'name': 'Noticeboard Grid',
        'description': 'Announcements and an image card grid for notice/news pages.',
        'layout_json': {
            'sections': [
                {'name': 'hero', 'label': 'Hero Banner'},
                {'name': 'notices', 'label': 'Notices'},
            ],
            'blocks': [
                {'element_id': 'board-hero', 'section': 'hero', 'type': 'hero'},
                {'element_id': 'announcements', 'section': 'notices', 'type': 'announcements'},
                {'element_id': 'story-grid', 'section': 'notices', 'type': 'card_grid'},
            ],
        },
    },
]

# URL name → system_key, kept in sync with SYSTEM_PAGES (the context
# processor uses this to find the CMS page for the current request).
SYSTEM_ROUTE_KEYS = {page['view_name']: page['key'] for page in SYSTEM_PAGES}


def register_system_pages():
    """Idempotently register core system pages, their feature blocks and the
    starter blueprints. Safe to call on every /builder/ visit."""
    created_pages = 0
    for spec in SYSTEM_PAGES:
        page, created = EditablePage.objects.get_or_create(
            system_key=spec['key'],
            defaults={
                'title': spec['title'],
                'slug': spec['slug'],
                'page_type': 'global',
                'is_published': True,
            },
        )
        if created:
            created_pages += 1
        elif page.title != spec['title']:
            # Keep the displayed title in sync without touching user content.
            page.title = spec['title']
            page.save(update_fields=['title', 'updated_at'])

        for index, block_spec in enumerate(spec['blocks']):
            ContentBlock.objects.get_or_create(
                page=page,
                element_id=block_spec['element_id'],
                defaults={
                    'block_type': block_spec['block_type'],
                    'content_json': block_spec['content_json'],
                    'visible': False,  # revealed by the admin from Block Manager
                    'order': index,
                },
            )

    for blueprint in BLUEPRINT_TEMPLATES:
        PageTemplate.objects.get_or_create(
            name=blueprint['name'],
            defaults={
                'description': blueprint['description'],
                'layout_json': blueprint['layout_json'],
            },
        )

    return created_pages
