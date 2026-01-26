package com.qutykarunia.erp.data.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.time.LocalDate

/**
 * Barcode Model
 */
data class ScannedBarcode(
    val format: String,
    val value: String,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Room Database Models
 */

@Entity(tableName = "offline_sync_queue")
data class OfflineSyncEntity(
    @PrimaryKey
    val id: String,
    val type: String, // "CARTON_CONFIRM", "DAILY_INPUT", etc
    val cartonId: String? = null,
    val spkId: Int? = null,
    val quantity: Int,
    val status: String = "PENDING", // PENDING, SENT, FAILED, COMPLETED
    val retryCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val payload: String? = null // JSON serialized request body
)

@Entity(tableName = "daily_production_cache")
data class DailyProductionCacheEntity(
    @PrimaryKey
    val id: String,
    val spkId: Int,
    val productionDate: LocalDate,
    val quantity: Int,
    val cumulativeQty: Int,
    val target: Int,
    val status: String = "LOCAL", // LOCAL, SYNCED, ERROR
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "finish_good_cache")
data class FinishGoodCacheEntity(
    @PrimaryKey
    val cartonId: String,
    val article: String,
    val quantity: Int,
    val status: String = "LOCAL", // LOCAL, SYNCED, ERROR
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "user_session")
data class UserSessionEntity(
    @PrimaryKey
    val userId: String,
    val username: String,
    val role: String,
    val jwtToken: String,
    val refreshToken: String,
    val tokenExpiresAt: Long,
    val lastActivity: Long = System.currentTimeMillis()
)

/**
 * API Request/Response Models
 */

// Authentication
data class LoginRequest(
    val username: String,
    val password: String,
    val pin: String? = null,
    val rfidCard: String? = null
)

data class LoginResponse(
    val success: Boolean,
    val user: UserData,
    val access_token: String,
    val refresh_token: String,
    val expires_in: Long
)

data class UserData(
    val id: String,
    val username: String,
    val full_name: String,
    val email: String,
    val role: String,
    val permissions: List<String>
)

// Production Models
data class ProductionInputRequest(
    val spk_id: Int,
    val production_date: LocalDate,
    val quantity: Int,
    val notes: String? = null
)

data class ProductionInputResponse(
    val success: Boolean,
    val data: ProductionInputData
)

data class ProductionInputData(
    val id: Int,
    val spk_id: Int,
    val quantity: Int,
    val cumulative_qty: Int,
    val target_qty: Int,
    val progress_pct: Float,
    val status: String
)

// SPK Models
data class SPKData(
    val id: Int,
    val spk_number: String,
    val product_name: String,
    val product_id: Int,
    val target_quantity: Int,
    val actual_quantity: Int,
    val status: String,
    val created_date: LocalDate,
    val due_date: LocalDate? = null,
    val completion_pct: Float = 0f,
    val assigned_to: String? = null
)

// Daily Production Grid
data class DailyProductionGridData(
    val spk_id: Int,
    val spk_number: String,
    val product: String,
    val targetQty: Int,
    val dailyInputs: Map<LocalDate, Int>, // Date -> Quantity
    val cumulativeTotal: Int,
    val progressPct: Float,
    val estimatedDaysRemaining: Int?
)

// Finish Good Models
data class FinishGoodShipmentData(
    val id: Int,
    val carton_id: String,
    val article: String,
    val quantity: Int,
    val barcode: String,
    val created_at: String,
    val status: String
)

data class CartonData(
    val id: String,
    val spk_id: Int,
    val article: String,
    val expected_quantity: Int,
    val articles: List<ArticleData>
)

data class ArticleData(
    val article_id: String,
    val article_name: String,
    val count: Int,
    val per_carton: Int
)

// Dashboard Models
data class DashboardData(
    val total_spks: Int,
    val in_progress: Int,
    val completed: Int,
    val on_track: Int,
    val at_risk: Int,
    val my_assignments: List<SPKData>
)

// Error Response
data class ErrorResponse(
    val success: Boolean = false,
    val message: String,
    val error_code: String? = null,
    val details: String? = null,
    val timestamp: String
)

/**
 * Barcode Formats
 */
enum class BarcodeFormat(val value: Int) {
    QR_CODE(1),
    CODE_128(2),
    EAN_13(3),
    CODE_39(4)
}

/**
 * Production Status
 */
enum class ProductionStatus(val displayName: String) {
    NOT_STARTED("Belum Dimulai"),
    IN_PROGRESS("Sedang Berjalan"),
    COMPLETED("Selesai"),
    ON_HOLD("Tunda"),
    CANCELLED("Dibatalkan")
}

/**
 * Sync Status for Offline Queue
 */
enum class SyncStatus(val value: String) {
    PENDING("PENDING"),
    SYNCING("SYNCING"),
    SYNCED("SYNCED"),
    FAILED("FAILED")
}
