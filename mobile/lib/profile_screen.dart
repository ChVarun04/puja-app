import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'api.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  static const _genders = ['Male', 'Female', 'Other'];
  static const _languages = [
    'English', 'Telugu', 'Hindi', 'Tamil', 'Kannada', 'Malayalam', 'Sanskrit'
  ];

  final _gotram = TextEditingController();
  final _nakshatram = TextEditingController();
  final _rashi = TextEditingController();
  final _country = TextEditingController();
  final _state = TextEditingController();
  final _city = TextEditingController();
  DateTime? _dob;
  String? _gender;
  String? _language;
  String _name = '', _email = '', _mobile = '';
  bool _loading = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final p = (await api.get('/me/profile')).data as Map;
      _name = p['full_name'] ?? '';
      _email = p['email'] ?? '';
      _mobile = p['mobile'] ?? '';
      _gotram.text = p['gotram'] ?? '';
      _nakshatram.text = p['nakshatram'] ?? '';
      _rashi.text = p['rashi'] ?? '';
      _country.text = p['country'] ?? '';
      _state.text = p['state'] ?? '';
      _city.text = p['city'] ?? '';
      _gender = p['gender'];
      _language = p['preferred_language'];
      if (p['dob'] != null) _dob = DateTime.tryParse(p['dob']);
    } catch (e) {
      if (mounted) toast(context, errorMessage(e));
    }
    if (mounted) setState(() => _loading = false);
  }

  String? _n(TextEditingController c) => c.text.trim().isEmpty ? null : c.text.trim();

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      await api.put('/me/profile', data: {
        'dob': _dob == null ? null : DateFormat('yyyy-MM-dd').format(_dob!),
        'gotram': _n(_gotram),
        'nakshatram': _n(_nakshatram),
        'rashi': _n(_rashi),
        'gender': _gender,
        'preferred_language': _language,
        'country': _n(_country),
        'state': _n(_state),
        'city': _n(_city),
      });
      if (!mounted) return;
      toast(context, 'Profile updated');
      Navigator.pop(context);
    } catch (e) {
      if (mounted) toast(context, errorMessage(e));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _pickDob() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _dob ?? DateTime(1990),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _dob = picked);
  }

  /// Keeps a saved value selectable even if it's not in our fixed list.
  List<DropdownMenuItem<String>> _items(List<String> base, String? current) {
    final list = [...base];
    if (current != null && !list.contains(current)) list.add(current);
    return list.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList();
  }

  Widget _field(String label, TextEditingController c) => Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: TextField(controller: c, decoration: InputDecoration(labelText: label)),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                    Card(
                      child: ListTile(
                        title: Text(_name,
                            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        subtitle: Text('$_email\n$_mobile'),
                        isThreeLine: true,
                      ),
                    ),
                    const SizedBox(height: 14),
                    InkWell(
                      onTap: _pickDob,
                      child: InputDecorator(
                        decoration: const InputDecoration(labelText: 'Date of birth'),
                        child: Text(_dob == null
                            ? 'Tap to select'
                            : DateFormat('dd MMM yyyy').format(_dob!)),
                      ),
                    ),
                    const SizedBox(height: 14),
                    DropdownButtonFormField<String>(
                      initialValue: _gender,
                      decoration: const InputDecoration(labelText: 'Gender'),
                      items: _items(_genders, _gender),
                      onChanged: (v) => setState(() => _gender = v),
                    ),
                    const SizedBox(height: 14),
                    DropdownButtonFormField<String>(
                      initialValue: _language,
                      decoration: const InputDecoration(labelText: 'Preferred language'),
                      items: _items(_languages, _language),
                      onChanged: (v) => setState(() => _language = v),
                    ),
                    const SizedBox(height: 14),
                    _field('Gotram', _gotram),
                    _field('Nakshatram', _nakshatram),
                    _field('Rashi', _rashi),
                    _field('Country', _country),
                    _field('State', _state),
                    _field('City', _city),
                    const SizedBox(height: 10),
                    FilledButton(
                      onPressed: _saving ? null : _save,
                      child: _saving
                          ? const SizedBox(
                              height: 24, width: 24,
                              child: CircularProgressIndicator(strokeWidth: 2))
                          : const Text('Save'),
                    ),
                  ]),
                ),
              ),
            ),
    );
  }
}