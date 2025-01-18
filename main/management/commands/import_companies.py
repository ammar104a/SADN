import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from main.models import Company  # Replace 'your_app' with your app name

class Command(BaseCommand):
    help = 'Import companies from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path']
        companies_created = 0
        companies_failed = 0

        self.stdout.write(f"\nStarting import at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("----------------------------------------")

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                # Verify the required columns exist
                required_columns = {'Name', 'Phone Number', 'Description', 'Website'}
                csv_columns = set(csv_reader.fieldnames)

                if not required_columns.issubset(csv_columns):
                    missing_columns = required_columns - csv_columns
                    self.stderr.write(f'Error: Missing required columns: {", ".join(missing_columns)}')
                    return

                for row in csv_reader:
                    try:
                        Company.objects.create(
                            name=row['Name'].strip(),
                            phone_number=row['Phone Number'].strip(),
                            description=row['Description'].strip(),
                            website=row['Website'].strip(),
                            company_type='PROSPECT',
                            location='',
                            industry=''
                        )
                        companies_created += 1
                        self.stdout.write(f"✓ Created: {row['Name']}")
                    except Exception as e:
                        companies_failed += 1
                        self.stderr.write(f"✗ Failed: {row['Name']} - Error: {str(e)}")

        except FileNotFoundError:
            self.stderr.write(f"Error: File not found at {csv_file_path}")
            return

        self.stdout.write("\nImport Summary:")
        self.stdout.write("----------------------------------------")
        self.stdout.write(f"Successfully created: {companies_created} companies")
        self.stdout.write(f"Failed to create: {companies_failed} companies")
        self.stdout.write(f"Total processed: {companies_created + companies_failed} companies")
        self.stdout.write(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

