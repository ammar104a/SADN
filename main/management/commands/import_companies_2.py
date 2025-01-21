# yourapp/management/commands/import_companies.py
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
import pandas as pd
from main.models import Company  # Update with your actual app name
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Import companies from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')
        parser.add_argument(
            '--skip-first-row',
            action='store_true',
            help='Skip the first row if it contains headers',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']

        # Print start time
        start_time = datetime.now()
        self.stdout.write(f"Starting import at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("-" * 40)

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            print(f"Detected columns: {df.columns.tolist()}")  # Debugging step

            # Field mapping from Excel columns to model fields
            field_mapping = {
                'Name': 'name',
                'Type': 'company_type',
                'Phone_Number': 'phone_number',
                'Location': 'location',
                'Website': 'website',
                'Industry': 'industry',
                'Description': 'description',
                'Facebook': 'facebook_url',
                'Instagram': 'instagram_handle',
                'Twitter': 'twitter_handle',
                'LinkedIn': 'linkedin_url',
                'Youtube': 'youtube_channel',
                'TikTok': 'tiktok_handle'
            }

            # Verify required columns exist
            required_columns = ['Name', 'Type', 'Phone_Number', 'Location', 'Industry', 'Description']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.stderr.write(self.style.ERROR(
                    f'Error: Missing required columns: {", ".join(missing_columns)}'
                ))
                return

            success_count = 0
            error_count = 0
            from django.core.validators import URLValidator
            from django.core.exceptions import ValidationError

            def clean_url(value):
                url_validator = URLValidator()
                try:
                    if value and isinstance(value, str):
                        url_validator(value.strip())  # Validate URL
                        return value.strip()
                except ValidationError:
                    return ""  # Return an empty string instead of None
                return ""

            # Process each row
            total_rows = len(df)
            import logging

            # Configure logging for errors
            logging.basicConfig(filename='import_errors.log', level=logging.ERROR)

            for idx, row in df.iterrows():
                try:
                    # Create company dict with mapped fields
                    company_data = {}
                    for excel_col, model_field in field_mapping.items():
                        if excel_col in df.columns:  # Only process if column exists
                            value = row.get(excel_col)
                            if pd.notna(value):
                                # Clean social media handles
                                if model_field in ['instagram_handle', 'twitter_handle', 'tiktok_handle']:
                                    value = str(value).strip('@')[:30]  # Truncate to 30 characters
                                # Validate and clean URLs
                                if model_field == 'website':
                                    value = clean_url(value)[:200]  # Clean and truncate URLs
                                # Default for blank descriptions
                                if model_field == 'description' and not value:
                                    value = 'No description provided'
                                company_data[model_field] = value

                    # Create and validate company instance
                    company = Company(**company_data)
                    company.full_clean()  # Validation
                    company.save()
                    success_count += 1

                    # Progress update
                    if (idx + 1) % 10 == 0:
                        self.stdout.write(f'Processed {idx + 1}/{total_rows} rows...')

                except ValidationError as e:
                    error_count += 1
                    error_message = f'Row {idx + 2}: Validation error - {str(e)}'
                    self.stderr.write(self.style.ERROR(error_message))
                    logging.error(f'{error_message} | Data: {row.to_dict()}')  # Log the row causing the error

                except Exception as e:
                    error_count += 1
                    error_message = f'Row {idx + 2}: Unexpected error - {str(e)}'
                    self.stderr.write(self.style.ERROR(error_message))
                    logging.error(f'{error_message} | Data: {row.to_dict()}')  # Log the row causing the error


        except Exception as e:
            self.stderr.write(self.style.ERROR(f'File processing error: {str(e)}'))