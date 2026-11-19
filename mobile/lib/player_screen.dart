import 'dart:math' as math;
import 'package:chewie/chewie.dart';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:video_player/video_player.dart';
import 'api.dart';

class PlayerScreen extends StatefulWidget {
  final Map<String, dynamic> media;
  const PlayerScreen({super.key, required this.media});
  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> {
  AudioPlayer? _audio;
  VideoPlayerController? _vc;
  ChewieController? _chewie;
  String? _error;
  bool _loading = true;

  bool get _isVideo => widget.media['content_type'] == 'video';

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      // Backend checks access and returns a short-lived signed URL
      final r = await api.get('/media/${widget.media['id']}/play-url');
      final url = r.data['url'] as String;
      if (_isVideo) {
        _vc = VideoPlayerController.networkUrl(Uri.parse(url));
        await _vc!.initialize();
        _chewie = ChewieController(
          videoPlayerController: _vc!,
          autoPlay: true,
          aspectRatio: _vc!.value.aspectRatio,
        );
      } else {
        _audio = AudioPlayer();
        await _audio!.setUrl(url);
        _audio!.play(); // not awaited: it completes only when audio ends
      }
    } catch (e) {
      _error = errorMessage(e);
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  void dispose() {
    _audio?.dispose();
    _chewie?.dispose();
    _vc?.dispose();
    super.dispose();
  }

  String _fmt(Duration d) {
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  Widget _audioUi() {
    final a = _audio!;
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        const Icon(Icons.self_improvement, size: 120, color: Color(0xFFE8750A)),
        const SizedBox(height: 16),
        Text(widget.media['title'] ?? '',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
        if ((widget.media['description'] ?? '').toString().isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(widget.media['description'], textAlign: TextAlign.center),
          ),
        const SizedBox(height: 24),
        StreamBuilder<Duration>(
          stream: a.positionStream,
          builder: (context, snap) {
            final pos = snap.data ?? Duration.zero;
            final dur = a.duration ?? Duration.zero;
            final max = dur.inMilliseconds > 0 ? dur.inMilliseconds.toDouble() : 1.0;
            return Column(children: [
              Slider(
                value: math.min(pos.inMilliseconds.toDouble(), max),
                max: max,
                onChanged: (v) => a.seek(Duration(milliseconds: v.toInt())),
              ),
              Row(mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [Text(_fmt(pos)), Text(_fmt(dur))]),
            ]);
          },
        ),
        const SizedBox(height: 8),
        StreamBuilder<PlayerState>(
          stream: a.playerStateStream,
          builder: (context, snap) {
            final playing = snap.data?.playing ?? false;
            return IconButton.filled(
              iconSize: 64,
              icon: Icon(playing ? Icons.pause : Icons.play_arrow),
              onPressed: () async {
                if (playing) {
                  a.pause();
                } else {
                  if (a.processingState == ProcessingState.completed) {
                    await a.seek(Duration.zero);
                  }
                  a.play();
                }
              },
            );
          },
        ),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.media['title'] ?? 'Player')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text(_error!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 18)),
                  ),
                )
              : _isVideo
                  ? Center(child: Chewie(controller: _chewie!))
                  : _audioUi(),
    );
  }
}