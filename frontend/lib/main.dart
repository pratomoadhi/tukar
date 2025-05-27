import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import 'package:flutter_pdfview/flutter_pdfview.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PDF Translator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
      ),
      home: const MyHomePage(title: 'PDF Translator App'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  File? _pdfFile;
  String _statusMessage = 'No file selected';
  bool _isLoading = false;
  String? _translatedPdfPath;

  // Function to pick a PDF file
  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom, 
      allowedExtensions: ['pdf']
    );
    if (result != null) {
      setState(() {
        _pdfFile = File(result.files.single.path!);
        _statusMessage = 'File selected: ${_pdfFile!.path.split('/').last}';
      });
    } else {
      setState(() {
        _statusMessage = 'No file selected';
      });
    }
  }

  // Function to send the file to the backend for translation
  Future<void> _translatePdf() async {
    if (_pdfFile == null) {
      setState(() {
        _statusMessage = 'Please select a PDF first.';
      });
      return;
    }

    // For Android 11 and above, check if the "MANAGE_EXTERNAL_STORAGE" permission is granted
    if (Platform.isAndroid && await Permission.manageExternalStorage.request().isGranted) {
      setState(() {
        _isLoading = true;
        _statusMessage = 'Translating...';
      });

      var uri = Uri.parse('http://10.0.2.2:8000/translate-pdf/'); // Your backend API
      var request = http.MultipartRequest('POST', uri)
        ..files.add(await http.MultipartFile.fromPath('file', _pdfFile!.path))
        ..fields['lang'] = 'id'; // Or 'ms' for Malay

      try {
        var response = await request.send();
        if (response.statusCode == 200) {
          var result = await response.stream.toBytes();
          
          // Get the path for the "Downloads" folder
          final downloadsDir = Directory('/storage/emulated/0/Download');
          if (!await downloadsDir.exists()) {
            await downloadsDir.create(recursive: true);
          }

          // Save the translated PDF to the Downloads folder
          var fileName = 'translated-${DateTime.now().millisecondsSinceEpoch}.pdf';
          String filePath = '${downloadsDir.path}/$fileName';
          File tempFile = File(filePath)..writeAsBytesSync(result);
          
          setState(() {
            _isLoading = false;
            _translatedPdfPath = tempFile.path;
            _statusMessage = 'Translation successful! Opening PDF...';
          });

          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => PDFViewerPage(path: _translatedPdfPath!),
            ),
          );
        } else {
          setState(() {
            _isLoading = false;
            _statusMessage = 'Failed to translate. Try again.';
          });
        }
      } catch (e) {
        setState(() {
          _isLoading = false;
          _statusMessage = 'Error: $e';
        });
      }
    } else {
      setState(() {
        _statusMessage = 'Permission to access storage denied.';
      });
    }
  }

  // Function to view the translated PDF
  Widget _buildPdfViewer() {
    if (_translatedPdfPath != null) {
      return Expanded( // Use Expanded to take available space
        child: PDFView(
          filePath: _translatedPdfPath,
          onPageChanged: (int? current, int? total) {},
          onError: (error) {
            print(error);
            setState(() {
              _statusMessage = 'Error loading PDF';
            });
          },
          onPageError: (page, error) {
            print('$page: $error');
          },
        ),
      );
    } else {
      return const Center(child: Text('No PDF to display'));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: <Widget>[
              Text(
                _statusMessage,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.black87,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                onPressed: _pickFile,
                icon: const Icon(Icons.upload_file),
                label: const Text('Pick PDF'),
              ),
              const SizedBox(height: 16),
              _isLoading
                  ? const Padding(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      child: CircularProgressIndicator(),
                    )
                  : ElevatedButton.icon(
                      onPressed: _translatePdf,
                      icon: const Icon(Icons.translate),
                      label: const Text('Translate PDF'),
                    ),
              const SizedBox(height: 24),
              if (_translatedPdfPath != null) _buildPdfViewer(),
            ],
          ),
        ),
      ),
    );
  }
}

class PDFViewerPage extends StatelessWidget {
  final String path;

  const PDFViewerPage({super.key, required this.path});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Translated PDF'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: PDFView(
        filePath: path,
        onError: (error) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to load PDF: $error')),
          );
        },
        onPageError: (page, error) {
          debugPrint('Page $page: $error');
        },
      ),
    );
  }
}
