package com.qutykarunia.erp.ui.components

import android.Manifest
import android.content.Context
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.LifecycleOwner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import timber.log.Timber
import java.util.concurrent.Executors

/**
 * Barcode Scanner Component using ML Kit
 * 
 * Supported formats:
 * - FORMAT_QR_CODE
 * - FORMAT_CODE_128
 * - FORMAT_EAN_13
 * - FORMAT_CODE_39
 * 
 * Real-time camera preview with live barcode detection
 */
@Composable
fun BarcodeScanner(
    onBarcodeScanned: (barcode: String) -> Unit,
    onError: (error: String) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    var scannedBarcodes by remember { mutableStateOf<List<String>>(emptyList()) }
    var lastScannedTime by remember { mutableStateOf(0L) }
    var hasPermission by remember { mutableStateOf(false) }
    
    // Request camera permission
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = androidx.activity.compose.ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasPermission = isGranted
        if (!isGranted) {
            onError("Camera permission denied")
        }
    }
    
    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }
    
    if (!hasPermission) {
        Box(
            modifier = modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.surface),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Camera permission required",
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = TextAlign.Center
            )
        }
        return
    }
    
    AndroidView(
        factory = { ctx ->
            PreviewView(ctx).apply {
                setupCameraAndBarcodeScan(
                    context = ctx,
                    lifecycleOwner = ctx as LifecycleOwner,
                    previewView = this,
                    onBarcodeScanned = { barcode ->
                        // Debounce: prevent rapid re-scans
                        val currentTime = System.currentTimeMillis()
                        if (currentTime - lastScannedTime > 1000) {
                            lastScannedTime = currentTime
                            if (!scannedBarcodes.contains(barcode)) {
                                scannedBarcodes = scannedBarcodes + barcode
                                onBarcodeScanned(barcode)
                                Timber.d("Barcode scanned: $barcode")
                            }
                        }
                    },
                    onError = onError
                )
            }
        },
        modifier = modifier.fillMaxSize()
    )
}

/**
 * Setup camera and barcode scanning
 */
private fun setupCameraAndBarcodeScan(
    context: Context,
    lifecycleOwner: LifecycleOwner,
    previewView: PreviewView,
    onBarcodeScanned: (String) -> Unit,
    onError: (String) -> Unit
) {
    val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
    
    cameraProviderFuture.addListener({
        try {
            val cameraProvider = cameraProviderFuture.get()
            
            // Setup preview
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            
            // Setup barcode analysis
            val barcodeAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also { analysis ->
                    analysis.setAnalyzer(
                        Executors.newSingleThreadExecutor()
                    ) { imageProxy ->
                        processImageForBarcode(
                            imageProxy = imageProxy,
                            onBarcodeScanned = onBarcodeScanned,
                            onError = onError
                        )
                    }
                }
            
            // Select back camera
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            
            // Bind to lifecycle
            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                barcodeAnalysis
            )
            
            Timber.d("Camera and barcode scanning setup complete")
            
        } catch (exc: Exception) {
            onError("Camera setup failed: ${exc.message}")
            Timber.e(exc, "Camera setup error")
        }
    }, { /* executor */ })
}

/**
 * Process image frame for barcode detection using ML Kit
 */
private fun processImageForBarcode(
    imageProxy: androidx.camera.core.ImageProxy,
    onBarcodeScanned: (String) -> Unit,
    onError: (String) -> Unit
) {
    try {
        val mediaImage = imageProxy.image ?: run {
            imageProxy.close()
            return
        }
        
        // Create InputImage from media image
        val image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )
        
        // Configure barcode scanner with supported formats
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_CODE_128,
                Barcode.FORMAT_EAN_13,
                Barcode.FORMAT_CODE_39
            )
            .build()
        
        val scanner = BarcodeScanning.getClient(options)
        
        scanner.process(image)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    val rawValue = barcode.rawValue
                    if (!rawValue.isNullOrEmpty()) {
                        onBarcodeScanned(rawValue)
                        Timber.d(
                            "Barcode detected - Format: ${barcode.format}, Value: $rawValue"
                        )
                    }
                }
            }
            .addOnFailureListener { exception ->
                onError("Barcode scanning failed: ${exception.message}")
                Timber.e(exception, "Barcode scanning error")
            }
            .addOnCompleteListener {
                imageProxy.close()
            }
        
    } catch (e: Exception) {
        onError("Image processing error: ${e.message}")
        Timber.e(e, "Image processing error")
        imageProxy.close()
    }
}

/**
 * Supported barcode formats reference
 * 
 * QR Code (PRIMARY):
 * - Contains carton ID and full shipment info
 * - Highest scanning accuracy
 * - Recommended format
 * 
 * Code128 (BACKUP):
 * - Carton barcode fallback
 * - Standard logistics barcode
 * 
 * EAN-13 (LABELS):
 * - Article/product identifier
 * - Per-item labels
 * 
 * Code39 (ALTERNATIVE):
 * - Alternative carton barcode format
 * - Some legacy systems use this
 */
