// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:medicine_assistant_app/main.dart';

void main() {
  testWidgets('Medicine Assistant app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MedicineAssistantApp());

    // Verify that the app title is displayed.
    expect(find.text('AI Medicine Assistant'), findsOneWidget);
    
    // Verify that the prescription input field is present.
    expect(find.byType(TextFormField), findsOneWidget);
    
    // Verify that the analyze button is present.
    expect(find.text('Analyze'), findsOneWidget);
  });
}
