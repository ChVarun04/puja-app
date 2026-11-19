import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'config.dart';

const _storage = FlutterSecureStorage();

Future<void> saveToken(String t) => _storage.write(key: 'token', value: t);
Future<void> clearToken() => _storage.delete(key: 'token');
Future<String?> getToken() => _storage.read(key: 'token');

final Dio api = Dio(BaseOptions(
  baseUrl: baseUrl,
  connectTimeout: const Duration(seconds: 60), // Render free tier may be waking up
  receiveTimeout: const Duration(seconds: 60),
))
  ..interceptors.add(InterceptorsWrapper(onRequest: (options, handler) async {
    final t = await getToken();
    if (t != null) options.headers['Authorization'] = 'Bearer $t';
    handler.next(options);
  }));

/// Turns any error into a short, readable message.
String errorMessage(Object e) {
  if (e is DioException) {
    final data = e.response?.data;
    if (data is Map && data['detail'] != null) {
      final d = data['detail'];
      if (d is String) return d; // e.g. "Email already registered"
      if (d is List && d.isNotEmpty) {
        // FastAPI 422 validation errors
        return d.map((x) {
          var msg = (x['msg'] ?? '').toString().replaceFirst('Value error, ', '');
          final loc = x['loc'];
          final field = (loc is List && loc.isNotEmpty) ? loc.last.toString() : '';
          return (field.isEmpty || field == 'body') ? msg : '$field: $msg';
        }).join('\n');
      }
    }
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'Server is waking up. Please try again in a few seconds.';
    }
    if (e.response == null) return 'Cannot reach the server. Check your internet.';
    return 'Error ${e.response?.statusCode}';
  }
  return 'Something went wrong';
}

void toast(BuildContext c, String m) =>
    ScaffoldMessenger.of(c).showSnackBar(SnackBar(content: Text(m)));