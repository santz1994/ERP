package com.qutykarunia.erp.data.api

import retrofit2.Response
import retrofit2.http.*
import com.qutykarunia.erp.data.models.*
import java.time.LocalDate

/**
 * Production API - Daily input and tracking
 */
interface ProductionApi {
    
    // Daily Production Input
    @POST("/api/v1/production/spk/{spk_id}/daily-input")
    suspend fun recordDailyInput(
        @Path("spk_id") spkId: Int,
        @Body request: DailyInputRequest
    ): Response<DailyInputResponse>

    // Get SPK Progress
    @GET("/api/v1/production/spk/{spk_id}/progress")
    suspend fun getSPKProgress(
        @Path("spk_id") spkId: Int
    ): Response<SPKProgressResponse>

    // Get My SPKs
    @GET("/api/v1/production/my-spks")
    suspend fun getMySPKs(
        @Query("status") status: String? = null
    ): Response<List<SPKResponse>>

    // Mobile variant
    @POST("/api/v1/production/mobile/daily-input")
    suspend fun mobileDailyInput(
        @Body request: MobileDailyInputRequest
    ): Response<MobileDailyInputResponse>
}

/**
 * PPIC API - Dashboard and monitoring (View-only)
 */
interface PPICApi {
    
    @GET("/api/v1/ppic/dashboard")
    suspend fun getPPICDashboard(): Response<PPICDashboardResponse>

    @GET("/api/v1/ppic/reports/daily-summary")
    suspend fun getDailySummary(): Response<DailySummaryResponse>

    @GET("/api/v1/ppic/reports/on-track-status")
    suspend fun getOnTrackStatus(): Response<OnTrackStatusResponse>

    @GET("/api/v1/ppic/alerts")
    suspend fun getAlerts(): Response<AlertsResponse>
}

/**
 * FinishGood API - Barcode scanning and carton management
 */
interface FinishGoodApi {
    
    @POST("/api/v1/warehouse/finishgood/receive")
    suspend fun receiveCarton(
        @Body request: CartonReceiveRequest
    ): Response<CartonReceiveResponse>

    @POST("/api/v1/warehouse/finishgood/verify")
    suspend fun verifyCarton(
        @Body request: CartonVerifyRequest
    ): Response<CartonVerifyResponse>

    @POST("/api/v1/warehouse/finishgood/confirm")
    suspend fun confirmCarton(
        @Body request: CartonConfirmRequest
    ): Response<CartonConfirmResponse>

    @GET("/api/v1/warehouse/finishgood/{id}")
    suspend fun getFinishGood(
        @Path("id") finishGoodId: Int
    ): Response<FinishGoodResponse>
}

/**
 * Request/Response Models
 */
data class DailyInputRequest(
    val production_date: LocalDate,
    val input_qty: Int,
    val notes: String? = null,
    val status: String = "CONFIRMED"
)

data class DailyInputResponse(
    val success: Boolean,
    val data: DailyInputData,
    val timestamp: String
)

data class DailyInputData(
    val cumulative_qty: Int,
    val target_qty: Int,
    val progress: Float,
    val message: String
)

data class MobileDailyInputRequest(
    val spk_id: Int,
    val production_date: LocalDate,
    val input_qty: Int,
    val notes: String? = null
)

data class MobileDailyInputResponse(
    val ok: Boolean,
    val id: Int,
    val qty: Int,
    val total: Int,
    val target: Int,
    val pct: Float
)

data class SPKResponse(
    val id: Int,
    val spk_number: String,
    val product: String,
    val target_qty: Int,
    val actual_qty: Int,
    val completion_pct: Float,
    val status: String,
    val created_date: String
)

data class SPKProgressResponse(
    val success: Boolean,
    val data: SPKProgressData,
    val timestamp: String
)

data class SPKProgressData(
    val target_qty: Int,
    val actual_qty: Int,
    val completion_pct: Float,
    val remaining_qty: Int,
    val status: String,
    val daily_entries: List<DailyEntry>,
    val summary: ProgressSummary
)

data class DailyEntry(
    val date: String,
    val qty: Int,
    val cumulative: Int,
    val status: String,
    val notes: String?
)

data class ProgressSummary(
    val total_days_tracked: Int,
    val avg_daily_rate: Float,
    val est_days_remaining: Int?
)

// PPIC Models
data class PPICDashboardResponse(
    val success: Boolean,
    val data: PPICDashboardData
)

data class PPICDashboardData(
    val dashboard: DashboardSummary,
    val spks: List<SPKStatus>
)

data class DashboardSummary(
    val total_spks: Int,
    val in_progress: Int,
    val completed: Int,
    val not_started: Int,
    val on_track: Int,
    val off_track: Int
)

data class SPKStatus(
    val spk_id: Int,
    val spk_number: String,
    val product: String,
    val target_qty: Int,
    val actual_qty: Int,
    val completion_pct: Float,
    val status: String,
    val health: String,
    val est_completion: String?
)

data class DailySummaryResponse(
    val success: Boolean,
    val data: DailySummaryData
)

data class DailySummaryData(
    val date: String,
    val target: Int,
    val actual: Int,
    val variance: Int,
    val by_stage: List<StageData>
)

data class StageData(
    val stage: String,
    val target: Int,
    val actual: Int,
    val variance: Int
)

data class OnTrackStatusResponse(
    val success: Boolean,
    val data: OnTrackStatusData
)

data class OnTrackStatusData(
    val on_track: Int,
    val at_risk: Int,
    val details: List<StatusDetail>
)

data class StatusDetail(
    val spk_id: Int,
    val status: String,
    val reason: String?
)

data class AlertsResponse(
    val success: Boolean,
    val data: AlertsData
)

data class AlertsData(
    val critical: List<Alert>,
    val warning: List<Alert>
)

data class Alert(
    val alert_id: Int,
    val spk_id: Int,
    val severity: String,
    val message: String,
    val created_at: String
)

// FinishGood Models
data class CartonReceiveRequest(
    val carton_id: String,
    val barcode: String,
    val article: String,
    val quantity: Int
)

data class CartonReceiveResponse(
    val success: Boolean,
    val carton_id: String,
    val message: String
)

data class CartonVerifyRequest(
    val carton_id: String,
    val article: String,
    val count: Int
)

data class CartonVerifyResponse(
    val success: Boolean,
    val verified: Boolean,
    val variance: Int?
)

data class CartonConfirmRequest(
    val carton_id: String,
    val final_qty: Int
)

data class CartonConfirmResponse(
    val success: Boolean,
    val finish_good_id: Int,
    val message: String
)

data class FinishGoodResponse(
    val success: Boolean,
    val data: FinishGoodData
)

data class FinishGoodData(
    val id: Int,
    val article: String,
    val quantity: Int,
    val status: String,
    val created_at: String
)
