import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

late List<CameraDescription> _cameras;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  _cameras = await availableCameras();
  runApp(const SentinelMobileApp());
}

class SentinelMobileApp extends StatelessWidget {
  const SentinelMobileApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark(),
      debugShowCheckedModeBanner: false,
      home: const CameraStreamingHome(),
    );
  }
}

class CameraStreamingHome extends StatefulWidget {
  const CameraStreamingHome({Key? key}) : super(key: key);

  @override
  State<CameraStreamingHome> createState() => _CameraStreamingHomeState();
}

class _CameraStreamingHomeState extends State<CameraStreamingHome> {
  CameraController? _controller;
  RawDatagramSocket? _udpSocket;
  ServerSocket? _tcpServer;
  Socket? _clientConnection;
  String _status = "Initializing Network Hooks...";
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _startDiscoveryBeacon();
  }

  void _initializeCamera() {
    if (_cameras.isEmpty) {
      setState(() => _status = "Hardware Error: No Camera Found");
      return;
    }
    _controller = CameraController(_cameras[0], ResolutionPreset.low, enableAudio: false);
    _controller!.initialize().then((_) {
      if (!mounted) return;
      setState(() {});
    });
  }

  void _startDiscoveryBeacon() async {
    try {
      _udpSocket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 8090);
      setState(() => _status = "Beacon Active: Awaiting Discovery...");
      
      _udpSocket!.listen((RawSocketEvent event) {
        if (event == RawSocketEvent.read) {
          Datagram? dg = _udpSocket!.receive();
          if (dg != null) {
            String message = utf8.decode(dg.data);
            if (message == "SENTINEL_DISCOVER") {
              _udpSocket!.send(utf8.encode("SENTINEL_NODE_HERE"), dg.address, dg.port);
              _stopDiscoveryAndStartTCP();
            }
          }
        }
      });
    } catch (e) {
      setState(() => _status = "Network Scan Fault: $e");
    }
  }

  void _stopDiscoveryAndStartTCP() async {
    _udpSocket?.close();
    try {
      _tcpServer = await ServerSocket.bind(InternetAddress.anyIPv4, 8089);
      setState(() => _status = "Discovered! Synchronizing Handshake...");
      
      _tcpServer!.listen((Socket client) {
        _clientConnection = client;
        setState(() => _status = "Streaming Active! Link Established.");
        _startStreamingFrames();
      });
    } catch (e) {
      setState(() => _status = "TCP Binding Failure: $e");
    }
  }

  void _startStreamingFrames() {
    if (_controller == null || !_controller!.value.isInitialized || _isStreaming) return;
    _isStreaming = true;

    _controller!.startImageStream((CameraImage image) async {
      if (_clientConnection == null) return;
      try {
        List<int> bytes = image.planes[0].bytes; 
        int length = bytes.length;
        
        var header = Uint8List(8);
        var byteData = ByteData.sublistView(header);
        byteData.setUint64(0, length, Endian.little);

        _clientConnection!.add(header);
        _clientConnection!.add(bytes);
        await _clientConnection!.flush();
      } catch (e) {
        _clientConnection?.close();
        _isStreaming = false;
        setState(() => _status = "Link Dropped. Resetting Beacon...");
        _startDiscoveryBeacon();
      }
    });
  }

  @override
  void dispose() {
    _controller?.dispose();
    _udpSocket?.close();
    _tcpServer?.close();
    _clientConnection?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return Scaffold(body: Center(child: Text(_status)));
    }
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(child: CameraPreview(_controller!)),
            Container(
              padding: const EdgeInsets.all(16),
              color: const Color(0xff1e293b),
              width: double.infinity,
              child: Text("Status: $_status", textAlign: TextAlign.center, style: const TextStyle(fontSize: 14, color: Colors.white)),
            )
          ],
        ),
      ),
    );
  }
}