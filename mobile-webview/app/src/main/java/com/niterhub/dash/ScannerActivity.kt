package com.niterhub.dash

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScanner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Full-screen native QR scanner using CameraX + ML Kit barcode detection.
 *
 * Launched from [MainActivity] via the `NiterHub.scanQR()` JS bridge when
 * the WebView's html5-qrcode library fails (getUserMedia is unreliable in
 * Android WebView). The scanned QR value is returned to the calling Activity
 * as [RESULT_OK] with the decoded string in [EXTRA_QR_RESULT].
 *
 * The scanner continuously analyses camera frames for QR/barcodes and stops
 * as soon as one is decoded (single-shot behaviour matching the attendance
 * use-case). The user can also tap the back button or the ✕ close button
 * to cancel.
 */
class ScannerActivity : AppCompatActivity() {

    companion object {
        /** Extra key for the decoded QR result returned to the caller. */
        const val EXTRA_QR_RESULT = "qr_result"
        private const val TAG = "ScannerActivity"
    }

    private lateinit var cameraPreview: PreviewView
    private lateinit var statusText: TextView
    private lateinit var closeButton: ImageButton
    private lateinit var cameraExecutor: ExecutorService
    private lateinit var barcodeScanner: BarcodeScanner

    /** Set to true once a barcode is decoded to prevent duplicate results. */
    @Volatile
    private var resultDelivered = false

    // ── Runtime permission launchers ──────────────────────────────────────
    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            startCamera()
        } else {
            Toast.makeText(this, "Camera permission is required to scan QR codes.", Toast.LENGTH_LONG).show()
            setResult(RESULT_CANCELED)
            finish()
        }
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_scanner)

        cameraPreview = findViewById(R.id.scanner_preview)
        statusText = findViewById(R.id.scanner_status)
        closeButton = findViewById(R.id.scanner_close_btn)

        closeButton.setOnClickListener {
            setResult(RESULT_CANCELED)
            finish()
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                setResult(RESULT_CANCELED)
                finish()
            }
        })

        // ML Kit barcode scanner configured for QR codes (and common 1D formats).
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_AZTEC,
                Barcode.FORMAT_DATA_MATRIX,
            )
            .build()
        barcodeScanner = BarcodeScanning.getClient(options)

        cameraExecutor = Executors.newSingleThreadExecutor()

        requestCameraPermissionAndStart()
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
        barcodeScanner.close()
    }

    // ── Camera setup ──────────────────────────────────────────────────────
    private fun requestCameraPermissionAndStart() {
        val perm = Manifest.permission.CAMERA
        if (ContextCompat.checkSelfPermission(this, perm) == PackageManager.PERMISSION_GRANTED) {
            startCamera()
        } else {
            cameraPermissionLauncher.launch(perm)
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder()
                .build()
                .also { it.surfaceProvider = cameraPreview.surfaceProvider }

            val imageAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also { analysis ->
                    analysis.setAnalyzer(cameraExecutor) { imageProxy ->
                        if (resultDelivered) {
                            imageProxy.close()
                            return@setAnalyzer
                        }
                        scanFrame(imageProxy)
                    }
                }

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    preview,
                    imageAnalysis,
                )
                statusText.text = "Point your camera at the QR code…"
            } catch (e: Exception) {
                Log.e(TAG, "Camera bind failed", e)
                Toast.makeText(this, "Camera could not start.", Toast.LENGTH_SHORT).show()
                setResult(RESULT_CANCELED)
                finish()
            }
        }, ContextCompat.getMainExecutor(this))
    }

    // ── Frame analysis ────────────────────────────────────────────────────
    @androidx.annotation.OptIn(androidx.camera.core.ExperimentalGetImage::class)
    private fun scanFrame(imageProxy: androidx.camera.core.ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees,
        )

        barcodeScanner.process(inputImage)
            .addOnSuccessListener { barcodes ->
                if (resultDelivered) return@addOnSuccessListener
                val barcode = barcodes.firstOrNull { bc ->
                    bc.valueType == Barcode.TYPE_URL ||
                    bc.valueType == Barcode.TYPE_TEXT ||
                    bc.valueType == Barcode.TYPE_UNKNOWN
                }
                if (barcode != null) {
                    val raw = barcode.rawValue ?: return@addOnSuccessListener
                    deliverResult(raw)
                }
            }
            .addOnFailureListener { e ->
                Log.w(TAG, "Barcode scan failed", e)
            }
            .addOnCompleteListener {
                // Always close the proxy regardless of success/failure.
                imageProxy.close()
            }
    }

    private fun deliverResult(value: String) {
        if (resultDelivered) return
        resultDelivered = true
        Log.i(TAG, "QR decoded: $value")
        val data = Intent().putExtra(EXTRA_QR_RESULT, value)
        setResult(RESULT_OK, data)
        finish()
    }
}
