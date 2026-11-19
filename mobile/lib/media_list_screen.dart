import 'package:flutter/material.dart';
import 'api.dart';
import 'player_screen.dart';

class MediaTile extends StatelessWidget {
  final Map<String, dynamic> media;
  const MediaTile({super.key, required this.media});

  @override
  Widget build(BuildContext context) {
    final isVideo = media['content_type'] == 'video';
    final lang = media['language'];
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Icon(isVideo ? Icons.videocam : Icons.headphones,
            size: 36, color: const Color(0xFFE8750A)),
        title: Text(media['title'] ?? '',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
        subtitle: Text('${lang != null ? '$lang • ' : ''}${media['content_type']}'),
        trailing: const Icon(Icons.play_circle_fill, size: 36),
        onTap: () => Navigator.push(
            context, MaterialPageRoute(builder: (_) => PlayerScreen(media: media))),
      ),
    );
  }
}

class MediaListScreen extends StatefulWidget {
  const MediaListScreen({super.key});
  @override
  State<MediaListScreen> createState() => _MediaListScreenState();
}

class _MediaListScreenState extends State<MediaListScreen> {
  List<Map<String, dynamic>> _items = [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final r = await api.get('/media', queryParameters: {'limit': 100});
      _items = List<Map<String, dynamic>>.from(r.data);
    } catch (e) {
      _error = errorMessage(e);
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('All My Content')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _items.isEmpty
                  ? const Center(child: Text('No content available yet.'))
                  : ListView(
                      padding: const EdgeInsets.all(16),
                      children: _items.map((m) => MediaTile(media: m)).toList(),
                    ),
    );
  }
}