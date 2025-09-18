import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MedicineAssistantApp());
}

class MedicineAssistantApp extends StatelessWidget {
  const MedicineAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Medicine Assistant',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const PrescriptionInputScreen(),
    );
  }
}

class PrescriptionInputScreen extends StatefulWidget {
  const PrescriptionInputScreen({super.key});

  @override
  State<PrescriptionInputScreen> createState() => _PrescriptionInputScreenState();
}

class _PrescriptionInputScreenState extends State<PrescriptionInputScreen> {
  final TextEditingController _prescriptionController = TextEditingController();
  bool _isLoading = false;
  String _responseMessage = '';
  Map<String, dynamic>? _analysisResult;

  // Django API base URL - update this to match your Django server
  static const String apiBaseUrl = 'http://127.0.0.1:8000/api';

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _responseMessage = '';
    });

    try {
      final response = await http.get(Uri.parse('$apiBaseUrl/ping/'));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _responseMessage = 'Connection successful: ${data['message']}';
        });
      } else {
        setState(() {
          _responseMessage = 'Connection failed: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _responseMessage = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _analyzePrescription() async {
    if (_prescriptionController.text.trim().isEmpty) {
      setState(() {
        _responseMessage = 'Please enter prescription text';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _responseMessage = '';
      _analysisResult = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/prescription/analyze/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': _prescriptionController.text}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _analysisResult = data;
          _responseMessage = 'Analysis completed successfully!';
        });
      } else {
        setState(() {
          _responseMessage = 'Analysis failed: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _responseMessage = 'Error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Medicine Assistant'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Enter your prescription:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _prescriptionController,
              maxLines: 4,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'e.g., Take Paracetamol 500mg twice daily for 3 days',
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _testConnection,
                    child: const Text('Test Connection'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _analyzePrescription,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Analyze Prescription'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_isLoading)
              const Center(
                child: CircularProgressIndicator(),
              ),
            if (_responseMessage.isNotEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    _responseMessage,
                    style: TextStyle(
                      color: _responseMessage.contains('successful') 
                          ? Colors.green 
                          : Colors.red,
                    ),
                  ),
                ),
              ),
            if (_analysisResult != null)
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Analysis Result:',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text('Input: ${_analysisResult!['input_text']}'),
                        const SizedBox(height: 8),
                        const Text(
                          'Extracted Medicines:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        ...(_analysisResult!['extracted_medicines'] as List).map(
                          (medicine) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Text(
                              '• ${medicine['name']} - ${medicine['dosage']} - ${medicine['frequency']} for ${medicine['duration']}',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _prescriptionController.dispose();
    super.dispose();
  }
}
