#!/bin/bash

# BioBERT Model Setup Script
# This script downloads the BioBERT model files required for the Medical Assistant Application

echo "🏥 Medical Assistant - BioBERT Model Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "ai-models" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Expected structure: med-assist/setup_biobert.sh"
    exit 1
fi

# Navigate to BioBERT directory
cd ai-models/biobert

# Check if model already exists
if [ -d "biobert-v1.1" ] && [ -f "biobert-v1.1/pytorch_model.bin" ]; then
    echo "✅ BioBERT model already exists!"
    echo "   Model files found in: ai-models/biobert/biobert-v1.1/"
    echo "   Size: $(du -sh biobert-v1.1/ | cut -f1)"
    echo ""
    echo "Do you want to re-download? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "✅ Using existing BioBERT model"
        exit 0
    fi
    echo "🗑️  Removing existing model..."
    rm -rf biobert-v1.1
fi

echo "📥 Downloading BioBERT model..."
echo "   Repository: dmis-lab/biobert-base-cased-v1.1"
echo "   Size: ~400MB"
echo "   This may take a few minutes..."
echo ""

# Method 1: Try git clone first
echo "🔄 Attempting Method 1: Git Clone..."
if git clone https://huggingface.co/dmis-lab/biobert-base-cased-v1.1 biobert-v1.1; then
    echo "✅ BioBERT model downloaded successfully using Git Clone!"
else
    echo "❌ Git clone failed. Trying alternative method..."
    
    # Method 2: Try huggingface_hub
    echo "🔄 Attempting Method 2: Hugging Face Hub..."
    if python -c "
import sys
try:
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id='dmis-lab/biobert-base-cased-v1.1', local_dir='biobert-v1.1')
    print('SUCCESS')
except ImportError:
    print('huggingface_hub not installed')
except Exception as e:
    print(f'Error: {e}')
"; then
        echo "✅ BioBERT model downloaded successfully using Hugging Face Hub!"
    else
        echo "❌ Both automated methods failed."
        echo ""
        echo "📋 Manual Download Instructions:"
        echo "1. Visit: https://huggingface.co/dmis-lab/biobert-base-cased-v1.1"
        echo "2. Click 'Files and versions'"
        echo "3. Download all files to: $(pwd)/biobert-v1.1/"
        echo "4. Required files:"
        echo "   - config.json"
        echo "   - pytorch_model.bin (~400MB)"
        echo "   - vocab.txt"
        echo "   - tokenizer_config.json"
        echo "   - special_tokens_map.json"
        echo "   - flax_model.msgpack"
        echo "   - .gitattributes"
        exit 1
    fi
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if [ -f "biobert-v1.1/pytorch_model.bin" ] && [ -f "biobert-v1.1/config.json" ] && [ -f "biobert-v1.1/vocab.txt" ]; then
    echo "✅ BioBERT model installation verified!"
    echo ""
    echo "📊 Model Information:"
    echo "   Location: $(pwd)/biobert-v1.1/"
    echo "   Size: $(du -sh biobert-v1.1/ | cut -f1)"
    echo "   Files: $(ls biobert-v1.1/ | wc -l) files"
    echo ""
    echo "🎉 BioBERT setup complete! You can now run the Medical Assistant Application."
    echo ""
    echo "Next steps:"
    echo "1. cd ../../backend"
    echo "2. python -m venv venv"
    echo "3. source venv/bin/activate"
    echo "4. pip install -r requirements.txt"
    echo "5. python manage.py migrate"
    echo "6. python manage.py runserver"
else
    echo "❌ Installation verification failed!"
    echo "   Missing required files in biobert-v1.1/"
    echo "   Please check the manual download instructions above."
    exit 1
fi
