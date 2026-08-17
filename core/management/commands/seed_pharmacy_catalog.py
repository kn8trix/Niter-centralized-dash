"""Seed the Online Pharmacy catalog with popular Bangladeshi medicines.

Populates ``MedicineItem`` rows for the storefront with realistic BD brands,
prices (BDT ৳), stock levels, expiry/batch data and detail-modal content
(usage / dosage / precautions / side effects / delivery estimate):

    python manage.py seed_pharmacy_catalog

**Idempotent by design:** every medicine is created with ``get_or_create``
keyed on the natural ``name`` + ``strength`` pair, so re-running never
duplicates rows. Existing rows (e.g. after an admin edits price/stock) are
left untouched — only the documented set is inserted when missing.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core.models import MedicineItem


def _expiry(years=2):
    """A far-future expiry date (2 years out by default)."""
    return date.today() + timedelta(days=365 * years)


# name, generic, strength, category, manufacturer, price, stock, rx,
# image text, description, usage, dosage, precautions, side effects, delivery
MEDICINES = [
    (
        'Napa Extra', 'Paracetamol + Caffeine', '500mg/65mg', 'tablet',
        'Square Pharmaceuticals', '20.00', 45, False,
        'Napa+Extra+500mg+65mg',
        'Fast-acting paracetamol with caffeine for fever and mild-to-moderate pain relief.',
        'Take with or after food. Swallow the tablet whole with water.',
        'Adults: 1 tablet every 4-6 hours as needed. Maximum 4 tablets in 24 hours.',
        'Do not exceed the stated dose. Avoid alcohol. Consult a doctor if you have liver disease.',
        'Nausea, stomach upset, or skin rash in rare cases.',
        '30-45 mins on campus',
    ),
    (
        'Seclo', 'Omeprazole', '20mg', 'capsule',
        'Square Pharmaceuticals', '50.00', 30, False,
        'Seclo+20mg+Omeprazole',
        'Proton pump inhibitor that reduces stomach acid — for acidity, heartburn and ulcers.',
        'Take 30 minutes before a meal, ideally in the morning. Swallow whole — do not chew or crush.',
        'Adults: 1 capsule once daily. Follow the doctor\u2019s direction for long-term use.',
        'Long-term use requires medical supervision. Inform your doctor about other medicines you take.',
        'Headache, diarrhoea, constipation or stomach pain.',
        '45-60 mins on campus',
    ),
    (
        'Sergel', 'Esomeprazole', '20mg', 'capsule',
        'Incepta Pharmaceuticals', '60.00', 25, False,
        'Sergel+20mg+Esomeprazole',
        'Acid-reducing capsule for heartburn, acid reflux and gastric ulcer treatment.',
        'Take at least 1 hour before a meal. Swallow whole with water.',
        'Adults: 20mg once daily for 4-8 weeks as directed by your physician.',
        'Not for children without medical advice. Avoid if allergic to esomeprazole or omeprazole.',
        'Headache, abdominal pain, flatulence or nausea.',
        '45-60 mins on campus',
    ),
    (
        'Ace Plus', 'Paracetamol', '500mg', 'tablet',
        'Beximco Pharmaceuticals', '8.00', 60, False,
        'Ace+Plus+500mg+Paracetamol',
        'Everyday paracetamol tablets for fever and pain — a trusted BD household brand.',
        'Take with water, with or without food.',
        'Adults and children over 12: 1-2 tablets every 4-6 hours. Max 8 tablets in 24 hours.',
        'Do not take with other paracetamol-containing products. Keep away from children.',
        'Rare; skin rash or nausea possible at high doses.',
        '30-45 mins on campus',
    ),
    (
        'Entacyd', 'Antacid (Chewable)', '—', 'tablet',
        'Square Pharmaceuticals', '10.00', 40, False,
        'Entacyd+Antacid+Chewable',
        'Chewable antacid tablets that neutralise stomach acid for fast acidity relief.',
        'Chew the tablet thoroughly before swallowing. Can be taken with or without water.',
        'Adults: 1-2 tablets after meals and at bedtime as needed. Do not exceed 8 tablets a day.',
        'Take other medicines 2 hours apart from this antacid.',
        'Constipation or mild stomach discomfort.',
        '15-30 mins on campus',
    ),
    (
        'Savlon Antiseptic Liquid', 'Chlorhexidine', '100ml', 'other',
        'ACI Limited', '120.00', 18, False,
        'Savlon+Antiseptic+Liquid+100ml',
        'Antiseptic liquid for cleaning minor cuts, wounds, and first-aid disinfection.',
        'Dilute 1 part Savlon in 30 parts water before use on skin or wounds.',
        'Apply the diluted solution to the affected area up to 2-3 times daily.',
        'For external use only. Do not swallow. Keep away from eyes.',
        'Skin irritation in sensitive individuals.',
        '45-60 mins on campus',
    ),
    (
        'Ceevit', 'Vitamin C', '250mg', 'tablet',
        'Square Pharmaceuticals', '35.00', 50, False,
        'Ceevit+250mg+Vitamin+C',
        'Vitamin C supplement to support immunity, skin health and iron absorption.',
        'Take after a meal with water.',
        'Adults: 1 tablet daily, or as directed by a physician.',
        'High doses may cause stomach upset; do not exceed recommended intake.',
        'Diarrhoea or stomach cramps in high doses.',
        '30-45 mins on campus',
    ),
    (
        'Monas', 'Montelukast', '10mg', 'tablet',
        'Acme Laboratories', '70.00', 0, True,
        'Monas+10mg+Montelukast',
        'Montelukast tablet for asthma and allergic rhinitis — prescription required.',
        'Take once daily in the evening, with or without food.',
        'Adults: 10mg once daily. Children: follow the doctor\u2019s prescribed dose.',
        'Rx required — do not use for acute asthma attacks. Consult your physician first.',
        'Headache, abdominal pain, or mild mood changes in rare cases.',
        'Rx verified before dispatch',
    ),
]


class Command(BaseCommand):
    help = 'Seed the pharmacy catalog with popular Bangladeshi medicines (idempotent).'

    # Local, self-hosted product photos (static/images/pharmacy/) — always
    # reachable, no external hotlink flakiness. The storefront falls back to
    # default_medicine.png if an image ever fails to load.
    IMAGE_URLS = {
        ('Napa Extra', '500mg/65mg'): '/static/images/pharmacy/napa_extra.png',
        ('Seclo', '20mg'): '/static/images/pharmacy/seclo.png',
        ('Sergel', '20mg'): '/static/images/pharmacy/sergel.png',
        ('Ace Plus', '500mg'): '/static/images/pharmacy/ace_plus.png',
        ('Entacyd', '—'): '/static/images/pharmacy/entacyd.png',
        ('Savlon Antiseptic Liquid', '100ml'): '/static/images/pharmacy/savlon.png',
        ('Ceevit', '250mg'): '/static/images/pharmacy/ceevit.png',
        ('Monas', '10mg'): '/static/images/pharmacy/monas.png',
    }

    def handle(self, *args, **options):
        created = 0
        for (name, generic, strength, category, manufacturer, price, stock,
             rx, image_text, description, usage, dosage, precautions,
             side_effects, delivery_eta) in MEDICINES:
            item, was_created = MedicineItem.objects.get_or_create(
                name=name,
                strength=strength,
                defaults={
                    'generic_name': generic,
                    'category': category,
                    'manufacturer': manufacturer,
                    'price': price,
                    'stock_quantity': int(stock),
                    'is_prescription': rx,
                    'image_url': self.IMAGE_URLS.get(
                        (name, strength),
                        '/static/images/pharmacy/default_medicine.png',
                    ),
                    'delivery_eta': delivery_eta,
                    'description': description,
                    'usage_info': usage,
                    'dosage_info': dosage,
                    'precautions': precautions,
                    'side_effects': side_effects,
                    'expiry_date': _expiry(),
                    'reorder_level': 10,
                    'is_active': True,
                },
            )
            if was_created:
                created += 1
                self.stdout.write('Created %s %s (%s)' % (name, strength, manufacturer))
            else:
                # Backfill rows seeded before this change: replace legacy
                # placehold.co placeholder URLs with the local product photo
                # (and keep the idempotent "don't clobber admin edits" rule —
                # only placeholder-looking URLs are touched).
                new_image = self.IMAGE_URLS.get(
                    (name, strength),
                    '/static/images/pharmacy/default_medicine.png',
                )
                if item.image_url and 'placehold.co' in item.image_url and item.image_url != new_image:
                    item.image_url = new_image
                    item.save(update_fields=['image_url'])
                    self.stdout.write('Backfilled image: %s %s' % (name, strength))
                else:
                    self.stdout.write('Exists (skipped): %s %s' % (name, strength))

        self.stdout.write(self.style.SUCCESS(
            'Pharmacy catalog seeded — %d new medicine(s), re-run safe.' % created
        ))
