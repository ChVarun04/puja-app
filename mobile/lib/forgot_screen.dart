import 'package:flutter/material.dart';
import 'api.dart';

class ForgotScreen extends StatefulWidget {
  const ForgotScreen({super.key});
  @override
  State<ForgotScreen> createState() => _ForgotScreenState();
}

class _ForgotScreenState extends State<ForgotScreen> {
  final _email = TextEditingController();
  final _token = TextEditingController();
  final _newPass = TextEditingController();
  bool _tokenReady = false;
  bool _loading = false;

  Future<void> _requestToken() async {
    if (_email.text.trim().isEmpty) {
      toast(context, 'Enter your email');
      return;
    }
    setState(() => _loading = true);
    try {
      final r = await api.post('/auth/forgot-password',
          queryParameters: {'email': _email.text.trim()});
      final t = r.data['reset_token'];
      if (!mounted) return;
      if (t == null) {
        toast(context, 'If the email exists, a reset token was generated');
      } else {
        _token.text = t; // demo only: a real app would email this token
        setState(() => _tokenReady = true);
      }
    } catch (e) {
      if (mounted) toast(context, errorMessage(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _reset() async {
    if (_newPass.text.length < 8) {
      toast(context, 'Password must be at least 8 characters');
      return;
    }
    setState(() => _loading = true);
    try {
      await api.post('/auth/reset-password',
          data: {'token': _token.text.trim(), 'new_password': _newPass.text});
      if (!mounted) return;
      toast(context, 'Password updated. Please log in.');
      Navigator.pop(context);
    } catch (e) {
      if (mounted) toast(context, errorMessage(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reset Password')),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: _email,
                  enabled: !_tokenReady,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(labelText: 'Registered email'),
                ),
                const SizedBox(height: 16),
                if (!_tokenReady)
                  FilledButton(
                    onPressed: _loading ? null : _requestToken,
                    child: const Text('Get reset token'),
                  ),
                if (_tokenReady) ...[
                  const Text(
                    'Demo mode: the reset token is filled in automatically '
                    '(a real app would email it).',
                    style: TextStyle(fontStyle: FontStyle.italic),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _token,
                    maxLines: 3,
                    decoration: const InputDecoration(labelText: 'Reset token'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _newPass,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'New password'),
                  ),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: _loading ? null : _reset,
                    child: const Text('Update password'),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}