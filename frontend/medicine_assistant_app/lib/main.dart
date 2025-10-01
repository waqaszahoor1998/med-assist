import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(const MedicineAssistantApp());
}

class MedicineAssistantApp extends StatelessWidget {
  const MedicineAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Medicine Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1976D2),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 2,
          titleTextStyle: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        cardTheme: CardThemeData(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const PrescriptionInputScreen(),
    const MedicalKnowledgeScreen(),
  ];

  final List<String> _titles = [
    'Prescription Analysis',
    'Medical Knowledge',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_selectedIndex]),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.medication),
            label: 'Prescription',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.library_books),
            label: 'Knowledge',
          ),
        ],
      ),
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
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  String _responseMessage = '';
  Map<String, dynamic>? _analysisResult;
  String? _errorMessage;
  Timer? _debounceTimer;

  // Django API base URL - update this to match your Django server
  static const String apiBaseUrl = 'http://127.0.0.1:8000/api';

  @override
  void dispose() {
    _prescriptionController.dispose();
    _debounceTimer?.cancel();
    super.dispose();
  }

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _responseMessage = '';
      _errorMessage = null;
    });

    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/ping/'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _responseMessage = 'Connection successful: ${data['message']}';
        });
        _showSnackBar('Backend connection established', isError: false);
      } else {
        setState(() {
          _errorMessage = 'Connection failed: ${response.statusCode}';
        });
        _showSnackBar('Backend connection failed', isError: true);
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
      });
      _showSnackBar('Unable to connect to backend', isError: true);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        duration: const Duration(seconds: 3),
        action: SnackBarAction(
          label: 'Dismiss',
          textColor: Colors.white,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }

  Future<void> _analyzePrescription() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_prescriptionController.text.trim().isEmpty) {
      _showSnackBar('Please enter prescription text', isError: true);
      return;
    }

    setState(() {
      _isLoading = true;
      _responseMessage = '';
      _analysisResult = null;
      _errorMessage = null;
    });

    try {
      // Use the new endpoint that includes drug interaction checking
      final response = await http.post(
        Uri.parse('$apiBaseUrl/prescription/analyze-with-safety/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': _prescriptionController.text.trim()}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _analysisResult = data;
          _responseMessage = 'Analysis completed successfully!';
        });
        _showSnackBar('Prescription analyzed successfully', isError: false);
      } else {
        final errorData = jsonDecode(response.body);
        setState(() {
          _errorMessage = 'Analysis failed: ${errorData['error'] ?? 'Unknown error'}';
        });
        _showSnackBar('Analysis failed', isError: true);
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
      });
      _showSnackBar('Network error occurred', isError: true);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<List<Map<String, dynamic>>> _getAlternatives(String medicineName) async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/alternatives/$medicineName/'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['alternatives'] ?? []);
      }
    } catch (e) {
      // Error fetching alternatives: $e
    }
    return [];
  }

  Future<void> _setReminder(String medicineName, String dosage, String frequency) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/reminders/set/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'medicine_name': medicineName,
          'dosage': dosage,
          'frequency': frequency,
          'time': '08:00',
          'user_id': 'default_user'
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(data['message'])),
          );
        }
      }
    } catch (e) {
      // Error setting reminder: $e
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('AI Medicine Assistant'),
        centerTitle: true,
        elevation: 4,
        actions: [
          IconButton(
            onPressed: _testConnection,
            icon: const Icon(Icons.wifi),
            tooltip: 'Test Connection',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
            // User Profile Card
            Card(
              color: Colors.purple.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    Icon(Icons.person, color: Colors.purple.shade700),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'User Profile',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.purple.shade700,
                            ),
                          ),
                          const Text('Age: 35, Weight: 70kg, Allergies: Penicillin'),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: _showUserProfile,
                      icon: Icon(Icons.edit, color: Colors.purple.shade700),
                    ),
                  ],
                ),
              ),
            ),
            
            // Header with database info
            if (_analysisResult != null)
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    children: [
                      Icon(Icons.science, color: Colors.blue.shade700),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Database: ${_analysisResult!['database_size']} medicines, ${_analysisResult!['structures_available']} with 3D structures',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue.shade700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            
            const SizedBox(height: 16),
            
            const Text(
              'Enter your prescription:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _prescriptionController,
              maxLines: 4,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter prescription text';
                }
                if (value.trim().length < 10) {
                  return 'Please enter a more detailed prescription';
                }
                return null;
              },
              decoration: InputDecoration(
                border: const OutlineInputBorder(),
                hintText: 'e.g., Take Metformin 500mg twice daily with meals',
                prefixIcon: const Icon(Icons.medication),
                suffixIcon: _prescriptionController.text.isNotEmpty
                    ? IconButton(
                        onPressed: () {
                          _prescriptionController.clear();
                          setState(() {
                            _analysisResult = null;
                            _responseMessage = '';
                            _errorMessage = null;
                          });
                        },
                        icon: const Icon(Icons.clear),
                      )
                    : null,
                errorMaxLines: 2,
              ),
              onChanged: (value) {
                setState(() {});
              },
            ),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _testConnection,
                    icon: const Icon(Icons.wifi),
                    label: const Text('Test Connection'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _analyzePrescription,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                    icon: const Icon(Icons.analytics),
                    label: const Text('Analyze'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_isLoading)
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      const CircularProgressIndicator(),
                      const SizedBox(height: 16),
                      const Text(
                        'Analyzing prescription with AI...',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'This may take a few moments',
                        style: TextStyle(fontSize: 14, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ),
            
            if (_responseMessage.isNotEmpty)
              Card(
                color: _responseMessage.contains('successful') 
                    ? Colors.green.shade50 
                    : Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      Icon(
                        _responseMessage.contains('successful') 
                            ? Icons.check_circle 
                            : Icons.error,
                        color: _responseMessage.contains('successful') 
                            ? Colors.green 
                            : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _responseMessage,
                          style: TextStyle(
                            color: _responseMessage.contains('successful') 
                                ? Colors.green.shade700 
                                : Colors.red.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            if (_errorMessage != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: Colors.red),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(
                            color: Colors.red.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      IconButton(
                        onPressed: () {
                          setState(() {
                            _errorMessage = null;
                          });
                        },
                        icon: const Icon(Icons.close, color: Colors.red),
                      ),
                    ],
                  ),
                ),
              ),
            
            if (_analysisResult != null)
              _buildAnalysisResult(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnalysisResult() {
    final medicines = _analysisResult!['extracted_medicines'] as List? ?? [];
    final molecularInfo = _analysisResult!['molecular_info'] as List? ?? [];
    final safetyAlerts = _analysisResult!['safety_alerts'] as List? ?? [];
    final interactions = _analysisResult!['interactions'] as List? ?? [];
    final confidenceScore = _analysisResult!['confidence_score'];
    final processingMethod = _analysisResult!['processing_method'] ?? 'Unknown';
    final aiModelInfo = _analysisResult!['ai_model_info'];
    final nlpVersion = _analysisResult!['nlp_version'] ?? 'Unknown';
    
    // New drug interaction data
    final drugInteractions = _analysisResult!['drug_interactions'];
    final safetyValidation = _analysisResult!['safety_validation'];

    // Convert confidence score to appropriate format
    double confidence = 0.0;
    if (confidenceScore is int) {
      confidence = confidenceScore / 100.0;
    } else if (confidenceScore is double) {
      confidence = confidenceScore;
    }

    bool isAI = processingMethod.contains('BioBERT') || processingMethod.contains('AI');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with AI processing info
            Row(
              children: [
                Icon(
                  isAI ? Icons.psychology : Icons.analytics,
                  color: isAI ? Colors.purple : Colors.blue,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Analysis Result',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: isAI ? Colors.purple : Colors.blue,
                        ),
                      ),
                      if (isAI)
                        Text(
                          'AI-Powered Analysis',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.purple,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: isAI ? Colors.purple : _getConfidenceColor((confidence * 100).round()),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Confidence: ${(confidence * 100).round()}%',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Input text
            Text(
              'Input: ${_analysisResult!['input_text']}',
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 16),
            
            // AI Model Information
            if (isAI && aiModelInfo != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.purple.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.psychology,
                          color: Colors.purple,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'AI Model Information',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.purple,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _buildInfoRow('Processing Method', processingMethod),
                    _buildInfoRow('NLP Version', nlpVersion),
                    if (aiModelInfo['model_parameters'] != null)
                      _buildInfoRow('Model Parameters', '${aiModelInfo['model_parameters'].toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')}'),
                    if (aiModelInfo['model_size_mb'] != null)
                      _buildInfoRow('Model Size', '${aiModelInfo['model_size_mb']} MB'),
                    if (aiModelInfo['status'] != null)
                      _buildInfoRow('Model Status', aiModelInfo['status']),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Data Sources Information
            if (_analysisResult!['data_sources'] != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.source,
                          color: Colors.blue,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Data Sources',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (_analysisResult!['data_sources']['medicine_extraction'] != null)
                      _buildInfoRow('Medicine Extraction', _analysisResult!['data_sources']['medicine_extraction']),
                    if (_analysisResult!['data_sources']['medicine_database'] != null)
                      _buildInfoRow('Medicine Database', _analysisResult!['data_sources']['medicine_database']),
                    if (_analysisResult!['data_sources']['drug_interactions'] != null)
                      _buildInfoRow('Drug Interactions', _analysisResult!['data_sources']['drug_interactions']),
                    if (_analysisResult!['data_sources']['medicine_info'] != null)
                      _buildInfoRow('Medicine Information', _analysisResult!['data_sources']['medicine_info']),
                    if (_analysisResult!['data_sources']['confidence_scoring'] != null)
                      _buildInfoRow('Confidence Scoring', _analysisResult!['data_sources']['confidence_scoring']),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            // Safety alerts
            if (safetyAlerts.isNotEmpty)
              _buildSafetyAlerts(safetyAlerts),
            
            // Drug interactions (new comprehensive system)
            if (drugInteractions != null && drugInteractions['interactions_found'] > 0)
              _buildDrugInteractionWarnings(drugInteractions),
            
            // Legacy drug interactions
            if (interactions.isNotEmpty)
              _buildInteractions(interactions),
            
            // Medicines list
            const Text(
              'Extracted Medicines:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            
            // Use a fixed height container for the medicines list
            SizedBox(
              height: 400, // Fixed height to make it scrollable
              child: ListView.builder(
                itemCount: medicines.length,
                itemBuilder: (context, index) {
                  final medicine = medicines[index];
                  final molecular = molecularInfo.isNotEmpty 
                      ? molecularInfo.firstWhere(
                          (m) => m['name'] == medicine['name'],
                          orElse: () => null,
                        )
                      : null;
                  
                  return _buildMedicineCard(medicine, molecular);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSafetyAlerts(List alerts) {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: Colors.red.shade700),
                const SizedBox(width: 8),
                Text(
                  'Safety Alerts',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ...alerts.map((alert) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2.0),
              child: Text('• $alert'),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractions(List interactions) {
    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning_amber, color: Colors.orange.shade700),
                const SizedBox(width: 8),
                Text(
                  'Drug Interactions',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ...interactions.map((interaction) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2.0),
              child: Text('• $interaction'),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildDrugInteractionWarnings(Map<String, dynamic> drugInteractions) {
    final interactions = drugInteractions['interactions'] as List? ?? [];
    final severitySummary = drugInteractions['severity_summary'] as Map<String, dynamic>? ?? {};
    final overallRisk = drugInteractions['overall_risk_level'] as String? ?? 'UNKNOWN';
    
    // Determine overall color based on risk level
    Color riskColor;
    IconData riskIcon;
    String riskTitle;
    
    switch (overallRisk.toUpperCase()) {
      case 'HIGH':
        riskColor = Colors.red;
        riskIcon = Icons.dangerous;
        riskTitle = 'HIGH RISK INTERACTIONS';
        break;
      case 'MEDIUM':
        riskColor = Colors.orange;
        riskIcon = Icons.warning;
        riskTitle = 'MEDIUM RISK INTERACTIONS';
        break;
      case 'LOW':
        riskColor = Colors.amber;
        riskIcon = Icons.info_outline;
        riskTitle = 'LOW RISK INTERACTIONS';
        break;
      case 'INFO':
        riskColor = Colors.blue;
        riskIcon = Icons.info;
        riskTitle = 'BENEFICIAL INTERACTIONS';
        break;
      default:
        riskColor = Colors.grey;
        riskIcon = Icons.help_outline;
        riskTitle = 'INTERACTIONS';
    }
    
    return Card(
      color: riskColor.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(riskIcon, color: riskColor, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    riskTitle,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: riskColor,
                      fontSize: 16,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: riskColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${interactions.length} Found',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            
            // Severity summary
            if (severitySummary.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: severitySummary.entries
                    .where((entry) => entry.value > 0)
                    .map((entry) => Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: _getSeverityColor(entry.key).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${entry.key}: ${entry.value}',
                            style: TextStyle(
                              color: _getSeverityColor(entry.key),
                              fontWeight: FontWeight.w500,
                              fontSize: 12,
                            ),
                          ),
                        ))
                    .toList(),
              ),
            ],
            
            const SizedBox(height: 12),
            
            // Individual interactions
            ...interactions.map((interaction) => _buildInteractionCard(interaction)),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractionCard(Map<String, dynamic> interaction) {
    final severity = interaction['severity'] as String? ?? 'UNKNOWN';
    final interactionType = interaction['interaction_type'] as String? ?? 'Unknown';
    final description = interaction['description'] as String? ?? '';
    final recommendation = interaction['recommendation'] as String? ?? '';
    final alternatives = interaction['alternatives'] as List? ?? [];
    final monitoring = interaction['monitoring'] as String? ?? '';
    
    final severityColor = _getSeverityColor(severity);
    final severityIcon = _getSeverityIcon(severity);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: severityColor.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: severityColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Interaction header
          Row(
            children: [
              Icon(severityIcon, color: severityColor, size: 16),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  interactionType,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: severityColor,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: severityColor,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  severity,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 6),
          
          // Description
          Text(
            description,
            style: const TextStyle(fontSize: 13),
          ),
          
          const SizedBox(height: 6),
          
          // Recommendation
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Recommendation:',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  recommendation,
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
          
          // Alternatives
          if (alternatives.isNotEmpty) ...[
            const SizedBox(height: 6),
            const Text(
              'Alternatives:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              alternatives.join(', '),
              style: const TextStyle(fontSize: 12),
            ),
          ],
          
          // Monitoring
          if (monitoring.isNotEmpty) ...[
            const SizedBox(height: 6),
            const Text(
              'Monitoring:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              monitoring,
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'HIGH':
        return Colors.red;
      case 'MEDIUM':
        return Colors.orange;
      case 'LOW':
        return Colors.amber;
      case 'INFO':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getSeverityIcon(String severity) {
    switch (severity.toUpperCase()) {
      case 'HIGH':
        return Icons.dangerous;
      case 'MEDIUM':
        return Icons.warning;
      case 'LOW':
        return Icons.info_outline;
      case 'INFO':
        return Icons.info;
      default:
        return Icons.help_outline;
    }
  }

  Widget _buildMedicineCard(Map<String, dynamic> medicine, Map<String, dynamic>? molecular) {
    // Get AI confidence score and source
    double confidence = medicine['confidence']?.toDouble() ?? 0.0;
    String source = medicine['source'] ?? 'Unknown';
    bool isAI = source.contains('BioBERT') || source.contains('AI');
    
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      child: ExpansionTile(
        leading: Icon(
          isAI ? Icons.psychology : (molecular != null ? Icons.science : Icons.medication),
          color: isAI ? Colors.purple : (molecular != null ? Colors.blue : Colors.grey),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                medicine['name'],
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            if (isAI) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.purple.withOpacity(0.3)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.psychology,
                      size: 12,
                      color: Colors.purple,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${(confidence * 100).toInt()}%',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        color: Colors.purple,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${medicine['dosage']} - ${medicine['frequency']} for ${medicine['duration']}',
            ),
            if (isAI)
              Text(
                'AI-powered extraction',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.purple,
                  fontWeight: FontWeight.w500,
                ),
              ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // AI Information
                if (isAI) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.purple.withOpacity(0.2)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.psychology,
                              color: Colors.purple,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'AI Analysis',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.purple,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        _buildInfoRow('Confidence Score', '${(confidence * 100).toInt()}%'),
                        _buildInfoRow('Processing Method', source),
                        _buildInfoRow('Extraction Source', 'BioBERT AI'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                
                // Basic info
                _buildInfoRow('Generic Name', medicine['generic_name'] ?? 'N/A'),
                _buildInfoRow('Indication', medicine['indication'] ?? 'N/A'),
                _buildInfoRow('Side Effects', medicine['side_effects'] ?? 'N/A'),
                
        // Show alternatives if available in the medicine data
        if (medicine['alternatives'] != null && 
            medicine['alternatives'].toString().isNotEmpty && 
            medicine['alternatives'] != 'Not available' &&
            medicine['alternatives'] != 'N/A')
          _buildInfoRow('Alternatives', medicine['alternatives']),
        
        // Add "Learn More" button for medical knowledge
        const SizedBox(height: 8),
        ElevatedButton.icon(
          onPressed: () => _showMedicalKnowledge(medicine['name']),
          icon: const Icon(Icons.library_books, size: 16),
          label: const Text('Learn More'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.purple,
            foregroundColor: Colors.white,
          ),
        ),
                
                
                // Data source information for detailed medicine data
                if (medicine['data_source'] != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.withOpacity(0.2)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.storage,
                              color: Colors.green,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Medicine Data Source',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        _buildInfoRow('Database', medicine['data_source'] ?? 'Unknown'),
                        if (medicine['source_details'] != null) ...[
                          _buildInfoRow('Origin', medicine['source_details']['origin'] ?? 'Unknown'),
                          _buildInfoRow('Last Updated', medicine['source_details']['last_updated'] ?? 'Unknown'),
                          _buildInfoRow('Reliability', medicine['source_details']['reliability'] ?? 'Unknown'),
                        ],
                      ],
                    ),
                  ),
                ],
                
                // Action buttons
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _setReminder(
                          medicine['name'],
                          medicine['dosage'],
                          medicine['frequency'],
                        ),
                        icon: const Icon(Icons.alarm),
                        label: const Text('Set Reminder'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _showAlternatives(medicine['name']),
                        icon: const Icon(Icons.compare_arrows),
                        label: const Text('Alternatives'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                
                // Molecular information
                if (molecular != null) ...[
                  const Divider(),
                  const Text(
                    'Molecular Information',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 8),
                  _buildInfoRow('Formula', molecular['molecular_formula'] ?? 'N/A'),
                  _buildInfoRow('Weight', '${molecular['molecular_weight']?.toStringAsFixed(2) ?? 'N/A'} g/mol'),
                  _buildInfoRow('CAS Number', molecular['cas_number'] ?? 'N/A'),
                  _buildInfoRow('UNII', molecular['unii'] ?? 'N/A'),
                  _buildInfoRow('Atoms', molecular['atom_count']?.toString() ?? 'N/A'),
                  _buildInfoRow('Bonds', molecular['bond_count']?.toString() ?? 'N/A'),
                  
                  // 3D Structure button
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () => _showMolecularViewer(molecular),
                      icon: const Icon(Icons.view_in_ar),
                      label: const Text('View 3D Structure'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ] else ...[
                  const Divider(),
                  const Text(
                    'No 3D structure available',
                    style: TextStyle(
                      fontStyle: FontStyle.italic,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, dynamic value) {
    String displayValue;
    
    if (value == null) {
      displayValue = 'N/A';
    } else if (value is List) {
      displayValue = value.join(', ');
    } else {
      displayValue = value.toString();
    }
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(displayValue),
          ),
        ],
      ),
    );
  }

  Color _getConfidenceColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  void _showMolecularViewer(Map<String, dynamic> molecular) {
    final formula = molecular['molecular_formula'] ?? '';
    final name = molecular['name'] ?? '';
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('3D Structure: $name'),
        content: SizedBox(
          width: 400,
          height: 400,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.science, size: 64, color: Colors.blue),
              const SizedBox(height: 16),
              Text('Molecular Formula: $formula'),
              const SizedBox(height: 8),
              Text('3D Structure Viewer'),
              const SizedBox(height: 8),
              Text('(WebView integration in progress)'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }


  void _showAlternatives(String medicineName) async {
    final alternatives = await _getAlternatives(medicineName);
    
    if (mounted) {
      showDialog(
        context: context,
      builder: (context) => AlertDialog(
        title: Text('Alternatives for $medicineName'),
        content: SizedBox(
          width: 400,
          height: 300,
          child: alternatives.isEmpty
              ? const Text('No alternatives found')
              : ListView.builder(
                  itemCount: alternatives.length,
                  itemBuilder: (context, index) {
                    final alt = alternatives[index];
                    return Card(
                      child: ListTile(
                        title: Text(alt['name'] ?? ''),
                        subtitle: Text(alt['generic_name'] ?? ''),
                        trailing: Text(
                          alt['estimated_price'] ?? '',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
    }
  }

  void _showUserProfile() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('User Profile'),
        content: const SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('👤 Personal Information'),
              SizedBox(height: 8),
              Text('Age: 35 years'),
              Text('Weight: 70 kg'),
              Text('Height: 170 cm'),
              SizedBox(height: 16),
              Text('⚠️ Allergies'),
              SizedBox(height: 8),
              Text('• Penicillin'),
              Text('• Sulfa drugs'),
              SizedBox(height: 16),
              Text('💊 Current Medications'),
              SizedBox(height: 8),
              Text('• Metformin 500mg daily'),
              Text('• Lisinopril 10mg daily'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showMedicalKnowledge(String medicineName) {
    // Navigate to medical knowledge screen with search
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => MedicalKnowledgeScreen(initialSearch: medicineName),
      ),
    );
  }

}

class MedicalKnowledgeScreen extends StatefulWidget {
  final String? initialSearch;
  
  const MedicalKnowledgeScreen({super.key, this.initialSearch});

  @override
  State<MedicalKnowledgeScreen> createState() => _MedicalKnowledgeScreenState();
}

class _MedicalKnowledgeScreenState extends State<MedicalKnowledgeScreen> {
  final TextEditingController _searchController = TextEditingController();
  bool _isLoading = false;
  List<dynamic> _searchResults = [];
  Map<String, dynamic>? _selectedMedicine;
  Map<String, dynamic>? _databaseStats;

  // Django API base URL
  static const String apiBaseUrl = 'http://127.0.0.1:8000/api';

  @override
  void initState() {
    super.initState();
    _loadDatabaseStats();
    
    // Set initial search if provided
    if (widget.initialSearch != null) {
      _searchController.text = widget.initialSearch!;
      _searchMedicalKnowledge(widget.initialSearch!);
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadDatabaseStats() async {
    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/medical-knowledge/stats/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _databaseStats = data;
        });
      }
    } catch (e) {
      print('Error loading database stats: $e');
    }
  }

  Future<void> _searchMedicalKnowledge(String query) async {
    if (query.trim().isEmpty) {
      setState(() {
        _searchResults = [];
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _searchResults = [];
    });

    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/medical-knowledge/search/?query=${Uri.encodeComponent(query)}'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _searchResults = data['results'] ?? [];
        });
      } else {
        _showSnackBar('Search failed: ${response.statusCode}', isError: true);
      }
    } catch (e) {
      _showSnackBar('Search error: ${e.toString()}', isError: true);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _getMedicineExplanation(String medicineName) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/medical-knowledge/explanation/${Uri.encodeComponent(medicineName)}/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _selectedMedicine = data;
        });
        _showMedicineExplanation(data);
      } else if (response.statusCode == 404) {
        _showSnackBar('No detailed explanation available for $medicineName', isError: true);
      } else {
        _showSnackBar('Failed to load explanation: ${response.statusCode}', isError: true);
      }
    } catch (e) {
      _showSnackBar('Error loading explanation: ${e.toString()}', isError: true);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showMedicineExplanation(Map<String, dynamic> medicine) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(medicine['medicine_name'] ?? 'Unknown Medicine'),
        content: SizedBox(
          width: 600,
          height: 500,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (medicine['generic_name'] != null)
                  _buildInfoRow('Generic Name', medicine['generic_name']),
                if (medicine['categories'] != null)
                  _buildInfoRow('Category', medicine['categories']),
                if (medicine['alternatives'] != null)
                  _buildInfoRow('Alternatives', medicine['alternatives']),
                if (medicine['knowledge_source'] != null)
                  _buildInfoRow('Source', medicine['knowledge_source']),
                const SizedBox(height: 16),
                const Text(
                  'Detailed Explanation:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  medicine['detailed_explanation'] ?? 'No explanation available',
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Medical Knowledge'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
        children: [
          // Database Stats Card
          if (_databaseStats != null)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Medical Knowledge Database',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('Total Medicines: ${_databaseStats!['statistics']['total_medicines']}'),
                    Text('With Detailed Explanations: ${_databaseStats!['statistics']['with_detailed_explanations']}'),
                    Text('Enhancement Coverage: ${_databaseStats!['statistics']['enhancement_coverage']}%'),
                  ],
                ),
              ),
            ),
          
          const SizedBox(height: 16),
          
          // Search Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Search Medical Knowledge',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Search for medicines, medical conditions, treatments, and symptoms',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          decoration: const InputDecoration(
                            hintText: 'Enter medicine name, condition, or symptom...',
                            border: OutlineInputBorder(),
                            prefixIcon: Icon(Icons.search),
                          ),
                          onChanged: (value) {
                            // Debounce search
                            Future.delayed(const Duration(milliseconds: 500), () {
                              if (_searchController.text == value) {
                                _searchMedicalKnowledge(value);
                              }
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: _isLoading ? null : () => _searchMedicalKnowledge(_searchController.text),
                        child: _isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Search'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Search Results
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _searchResults.isEmpty
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.search, size: 64, color: Colors.grey),
                            SizedBox(height: 16),
                            Text(
                              'Enter a search term to explore medical knowledge',
                              style: TextStyle(fontSize: 16, color: Colors.grey),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        itemCount: _searchResults.length,
                        itemBuilder: (context, index) {
                          final result = _searchResults[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 4),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: result['has_detailed_explanation']
                                    ? Colors.green
                                    : Colors.grey,
                                child: Icon(
                                  result['has_detailed_explanation']
                                      ? Icons.medical_services
                                      : Icons.info,
                                  color: Colors.white,
                                ),
                              ),
                              title: Text(result['name'] ?? 'Unknown'),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (result['generic_name'] != null)
                                    Text('Generic: ${result['generic_name']}'),
                                  if (result['categories'] != null)
                                    Text('Category: ${result['categories']}'),
                                  if (result['explanation_length'] > 0)
                                    Text('Explanation: ${result['explanation_length']} characters'),
                                ],
                              ),
                              trailing: result['has_detailed_explanation']
                                  ? ElevatedButton(
                                      onPressed: () => _getMedicineExplanation(result['name']),
                                      child: const Text('Learn More'),
                                    )
                                  : const Text('Limited Info'),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
      ),
    );
  }
}