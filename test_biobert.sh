#!/bin/bash

# BioBERT Model Test Script
# This script tests if the BioBERT model is properly installed and working

echo "🧪 Medical Assistant - BioBERT Model Test"
echo "========================================="

# Check if we're in the right directory
if [ ! -d "ai-models" ]; then
    echo " Error: Please run this script from the project root directory"
    exit 1
fi

# Check if BioBERT model exists
if [ ! -d "ai-models/biobert/biobert-v1.1" ]; then
    echo "❌ BioBERT model not found!"
    echo "   Please run: ./setup_biobert.sh"
    exit 1
fi

echo "🔍 Checking BioBERT model files..."

# Check for required files
required_files=(
    "ai-models/biobert/biobert-v1.1/config.json"
    "ai-models/biobert/biobert-v1.1/pytorch_model.bin"
    "ai-models/biobert/biobert-v1.1/vocab.txt"
    "ai-models/biobert/biobert-v1.1/tokenizer_config.json"
    "ai-models/biobert/biobert-v1.1/special_tokens_map.json"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $(basename "$file")"
    else
        echo "❌ $(basename "$file") - MISSING"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ Some required files are missing!"
    echo "   Please run: ./setup_biobert.sh"
    exit 1
fi

echo ""
echo "📊 Model Information:"
echo "   Location: ai-models/biobert/biobert-v1.1/"
echo "   Size: $(du -sh ai-models/biobert/biobert-v1.1/ | cut -f1)"
echo "   Files: $(ls ai-models/biobert/biobert-v1.1/ | wc -l) files"

# Test Python import
echo ""
echo "🐍 Testing Python import..."
if python -c "
import sys
sys.path.append('backend')
try:
    from api.biobert_processor import get_biobert_processor
    processor = get_biobert_processor()
    print('✅ BioBERT processor loaded successfully!')
    print(f'   Model type: {type(processor)}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('   Make sure you are in the project root directory')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error loading BioBERT: {e}')
    sys.exit(1)
"; then
    echo "✅ BioBERT model test passed!"
    echo ""
    echo "🎉 BioBERT is ready to use!"
    echo "   You can now run the Medical Assistant Application."
else
    echo "❌ BioBERT model test failed!"
    echo "   Please check the installation and try again."
    exit 1
fi
