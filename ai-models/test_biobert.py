#!/usr/bin/env python3
"""
Test BioBERT model with sample prescriptions
Based on the official HuggingFace notebook
"""

from transformers import AutoTokenizer, AutoModel, pipeline
import torch

def test_biobert_basic():
    """Test basic BioBERT functionality"""
    print("=" * 50)
    print("Testing BioBERT Basic Setup")
    print("=" * 50)
    
    # Load model and tokenizer
    print("Loading BioBERT model...")
    tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
    model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1")
    
    print("✅ Model loaded successfully!")
    print(f"Tokenizer vocab size: {tokenizer.vocab_size}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    return tokenizer, model

def test_biobert_pipeline():
    """Test BioBERT using the pipeline approach"""
    print("\n" + "=" * 50)
    print("Testing BioBERT Pipeline")
    print("=" * 50)
    
    # Use pipeline for feature extraction
    pipe = pipeline("feature-extraction", model="dmis-lab/biobert-v1.1")
    
    # Test with sample prescriptions
    test_prescriptions = [
        "Take Metformin 500mg twice daily with meals",
        "Aspirin 81mg once daily for heart health",
        "Amoxicillin 250mg three times daily for 7 days",
        "Take Ibuprofen 200mg as needed for pain"
    ]
    
    for i, prescription in enumerate(test_prescriptions, 1):
        print(f"\nTest {i}: {prescription}")
        result = pipe(prescription)
        print(f"✅ Pipeline working! Output shape: {len(result[0])} features")
    
    return pipe

def test_prescription_analysis(tokenizer, model):
    """Test detailed prescription analysis"""
    print("\n" + "=" * 50)
    print("Testing Detailed Prescription Analysis")
    print("=" * 50)
    
    test_text = "Take Metformin 500mg twice daily with meals"
    print(f"Analyzing: '{test_text}'")
    
    # Tokenize the prescription
    inputs = tokenizer(test_text, return_tensors="pt", truncation=True, max_length=512)
    
    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)
    
    print(f"✅ Analysis complete!")
    print(f"Input tokens: {inputs['input_ids'].shape[1]}")
    print(f"Output features: {outputs.last_hidden_state.shape}")
    print(f"Feature dimensions: {outputs.last_hidden_state.shape[2]}")
    
    # Show tokenization details
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    print(f"\nTokenized text: {tokens[:10]}...")  # Show first 10 tokens
    
    return outputs

def main():
    """Main test function"""
    print("🧬 BioBERT Medicine Assistant Test")
    print("Testing the AI model for prescription analysis")
    
    try:
        # Test 1: Basic setup
        tokenizer, model = test_biobert_basic()
        
        # Test 2: Pipeline approach
        pipe = test_biobert_pipeline()
        
        # Test 3: Detailed analysis
        outputs = test_prescription_analysis(tokenizer, model)
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("BioBERT is ready for integration with your Django backend")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("Please check your internet connection and try again")

if __name__ == "__main__":
    main()
