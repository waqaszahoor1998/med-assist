from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from api.models import Medicine, MedicalKnowledge


class Command(BaseCommand):
    help = 'Populate database with medicine and medical knowledge data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--medicines-file',
            type=str,
            default='../datasets/processed/enhanced_ultimate_medicine_database.json',
            help='Path to medicines database JSON file'
        )
        parser.add_argument(
            '--medical-knowledge-file',
            type=str,
            default='../datasets/processed/wiki_medical_knowledge.json',
            help='Path to medical knowledge JSON file'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for database operations'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Get file paths
        medicines_file = options['medicines_file']
        medical_knowledge_file = options['medical_knowledge_file']
        batch_size = options['batch_size']
        
        # Check if files exist
        if not os.path.exists(medicines_file):
            self.stdout.write(
                self.style.ERROR(f'Medicines file not found: {medicines_file}')
            )
            return
            
        if not os.path.exists(medical_knowledge_file):
            self.stdout.write(
                self.style.WARNING(f'Medical knowledge file not found: {medical_knowledge_file}')
                + ' - Skipping medical knowledge import'
            )
        
        # Import medicines
        self.import_medicines(medicines_file, batch_size)
        
        # Import medical knowledge if file exists
        if os.path.exists(medical_knowledge_file):
            self.import_medical_knowledge(medical_knowledge_file, batch_size)
        
        self.stdout.write(self.style.SUCCESS('Database population completed!'))

    def import_medicines(self, file_path, batch_size):
        """Import medicines from JSON file"""
        self.stdout.write('Importing medicines...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            medicines_data = json.load(f)
        
        medicines = medicines_data.get('medicines', [])
        total_medicines = len(medicines)
        
        self.stdout.write(f'Found {total_medicines} medicines to import')
        
        # Clear existing medicines
        Medicine.objects.all().delete()
        self.stdout.write('Cleared existing medicine data')
        
        # Import in batches
        imported_count = 0
        for i in range(0, total_medicines, batch_size):
            batch = medicines[i:i + batch_size]
            medicine_objects = []
            
            for medicine_data in batch:
                try:
                    # Handle different data formats
                    if isinstance(medicine_data, dict):
                        medicine_obj = Medicine(
                            name=medicine_data.get('name', ''),
                            generic_name=medicine_data.get('generic_name', ''),
                            brand_names=medicine_data.get('brand_names', []),
                            category=medicine_data.get('category', ''),
                            description=medicine_data.get('description', ''),
                            common_doses=medicine_data.get('common_doses', []),
                            side_effects=medicine_data.get('side_effects', []),
                            interactions=medicine_data.get('interactions', []),
                            contraindications=medicine_data.get('contraindications', []),
                            alternatives=medicine_data.get('alternatives', []),
                            cost_analysis=medicine_data.get('cost_analysis', {}),
                            molecular_structure=medicine_data.get('molecular_structure', {}),
                            medical_explanation=medicine_data.get('medical_explanation', ''),
                            data_sources=medicine_data.get('data_sources', [])
                        )
                        medicine_objects.append(medicine_obj)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing medicine: {e}')
                    )
                    continue
            
            # Bulk create batch
            if medicine_objects:
                Medicine.objects.bulk_create(medicine_objects, ignore_conflicts=True)
                imported_count += len(medicine_objects)
                
            # Progress update
            progress = min(100, (i + len(batch)) / total_medicines * 100)
            self.stdout.write(f'Progress: {progress:.1f}% ({imported_count} medicines imported)')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} medicines')
        )

    def import_medical_knowledge(self, file_path, batch_size):
        """Import medical knowledge from JSON file"""
        self.stdout.write('Importing medical knowledge...')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        
        knowledge_entries = knowledge_data.get('medical_knowledge', [])
        total_entries = len(knowledge_entries)
        
        self.stdout.write(f'Found {total_entries} medical knowledge entries to import')
        
        # Clear existing medical knowledge
        MedicalKnowledge.objects.all().delete()
        self.stdout.write('Cleared existing medical knowledge data')
        
        # Import in batches
        imported_count = 0
        for i in range(0, total_entries, batch_size):
            batch = knowledge_entries[i:i + batch_size]
            knowledge_objects = []
            
            for entry_data in batch:
                try:
                    knowledge_obj = MedicalKnowledge(
                        term=entry_data.get('term', ''),
                        explanation=entry_data.get('explanation', ''),
                        category=entry_data.get('category', ''),
                        related_terms=entry_data.get('related_terms', []),
                        source=entry_data.get('source', 'Wiki')
                    )
                    knowledge_objects.append(knowledge_obj)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing knowledge entry: {e}')
                    )
                    continue
            
            # Bulk create batch
            if knowledge_objects:
                MedicalKnowledge.objects.bulk_create(knowledge_objects, ignore_conflicts=True)
                imported_count += len(knowledge_objects)
                
            # Progress update
            progress = min(100, (i + len(batch)) / total_entries * 100)
            self.stdout.write(f'Progress: {progress:.1f}% ({imported_count} entries imported)')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} medical knowledge entries')
        )
