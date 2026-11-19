import 'package:flutter/material.dart';
import 'api.dart';
import 'login_screen.dart';
import 'dashboard_screen.dart';

void main() => runApp(const PujaApp());

class PujaApp extends StatelessWidget {
  const PujaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Puja App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFE8750A)),
        scaffoldBackgroundColor: const Color(0xFFFFF7EC),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFE8750A),
          foregroundColor: Colors.white,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
          filled: true,
          fillColor: Colors.white,
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(56),
            textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          ),
        ),
      ),
      // Bigger text for elderly users
      builder: (context, child) => MediaQuery(
        data: MediaQuery.of(context).copyWith(textScaler: const TextScaler.linear(1.15)),
        child: child!,
      ),
      home: const Gate(),
    );
  }
}

/// Decides the first screen: logged in -> dashboard, else login.
class Gate extends StatelessWidget {
  const Gate({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: getToken(),
      builder: (context, snap) {
        if (snap.connectionState != ConnectionState.done) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        return snap.data == null ? const LoginScreen() : const DashboardScreen();
      },
    );
  }
}