import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'api.dart';
import 'login_screen.dart';
import 'profile_screen.dart';
import 'media_list_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _d;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final r = await api.get('/me/dashboard');
      _d = Map<String, dynamic>.from(r.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        await _logout();
        return;
      }
      _error = errorMessage(e);
    } catch (e) {
      _error = errorMessage(e);
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _logout() async {
    await clearToken();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(context,
        MaterialPageRoute(builder: (_) => const LoginScreen()), (_) => false);
  }

  Widget _chip(String label, dynamic value) => Chip(
        backgroundColor: Colors.white,
        label: Text('$label: ${value ?? '—'}', style: const TextStyle(fontSize: 15)),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Puja'),
        actions: [
          IconButton(
            tooltip: 'Profile',
            icon: const Icon(Icons.person),
            onPressed: () async {
              await Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const ProfileScreen()));
              _load(); // refresh after profile edit
            },
          ),
          IconButton(tooltip: 'Logout', icon: const Icon(Icons.logout), onPressed: _logout),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(mainAxisSize: MainAxisSize.min, children: [
                      Text(_error!, textAlign: TextAlign.center),
                      const SizedBox(height: 12),
                      FilledButton(onPressed: _load, child: const Text('Retry')),
                    ]),
                  ),
                )
              : RefreshIndicator(onRefresh: _load, child: _content()),
    );
  }

  Widget _content() {
    final d = _d!;
    final deity = d['deity'] as Map<String, dynamic>?;
    final media = List<Map<String, dynamic>>.from(d['media'] ?? []);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Welcome card
        Card(
          color: const Color(0xFFE8750A),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(d['welcome'] ?? '',
                  style: const TextStyle(
                      color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Text('${d['weekday']}, ${d['date']}',
                  style: const TextStyle(color: Colors.white, fontSize: 17)),
            ]),
          ),
        ),
        const SizedBox(height: 8),
        Wrap(spacing: 8, children: [
          _chip('Gotram', d['gotram']),
          _chip('Nakshatram', d['nakshatram']),
          _chip('Rashi', d['rashi']),
        ]),
        if (d['gotram'] == null && d['nakshatram'] == null && d['rashi'] == null)
          const Padding(
            padding: EdgeInsets.only(top: 6),
            child: Text('Tip: tap the profile icon to add your Gotram, Nakshatram and Rashi.'),
          ),
        const SizedBox(height: 12),

        // Weekday deity (comes from the DB, changes with the admin mapping)
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: deity == null
                ? const Text('No deity is mapped for today.')
                : Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Text("Today's Deity",
                        style: TextStyle(fontSize: 14, color: Colors.black54)),
                    const SizedBox(height: 4),
                    Text(deity['name'] ?? '',
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Text(deity['description'] ?? ''),
                  ]),
          ),
        ),
        const SizedBox(height: 16),

        const Text("Today's Devotional Content",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        if (media.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: Text('No content for today yet.'),
          ),
        ...media.map((m) => MediaTile(media: m)),
        const SizedBox(height: 16),
        FilledButton.icon(
          icon: const Icon(Icons.library_music),
          label: const Text('All my content'),
          onPressed: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const MediaListScreen())),
        ),
      ],
    );
  }
}