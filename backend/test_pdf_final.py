from datetime import date
from app.weber.pdf import build_offer_pdf

doc = type('Doc', (), {
    'id': 'test-id',
    'number': 'TEST-001',
    'customer_id': 'C-001',
    'offer_date': date(2026, 1, 15),
    'status': 'Pending response',
    'inspection_frequency': 'Annual',
    'responsible_person': 'Test User',
    'subsidiary_id': 'Weber Iberica',
    'account_name': 'Test Customer',
    'account_city': 'Madrid',
    'account_province': 'Madrid',
    'account_country': 'Spain',
    'currency': 'EUR',
    'trip_cost': 100,
    'diets': 50,
    'hotel_cost': 100,
    'trip_hours': 6,
    'work_hours': 10,
    'bk_hours': 0,
    'report_hours': 2,
    'km': 100,
    'km_rate': 0.5,
    'tech_rate': 105,
    'diet_full_rate': 40,
    'diet_half_rate': 20,
    'hotel_rate': 80,
    'discount_rate': 0.15,
    'bk_price': 0,
    'total': 1050,
    'total_end': 906,
    'general_comments': None,
    'lines': [],
    'guardian_selections': ['maintenance_inspection'],
    'customer_id': 'C-001',
    'id_guardian_offer': 'TEST-001',
    'id': 'test-id',
    'created_at': None,
    'updated_at': None,
    'customer_site': 'Test Site',
    'language': 'es',
    'customer_number': 'C-001',
    'discount': 157.5,
    'discount_rate': 0.15,
    'hours_import': 2520.0,
    'expenses': 340.0,
    'total': 2860.0,
    'total_end': 2860.0,
})()

from app.weber.pdf import build_offer_pdf
pdf_bytes = build_offer_pdf(doc)
print(f'PDF generated: {len(pdf_bytes)} bytes')
assert len(pdf_bytes) > 1000
print('PDF generated successfully')