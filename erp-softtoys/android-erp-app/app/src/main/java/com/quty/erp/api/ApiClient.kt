package com.quty.erp.api

import com.google.gson.GsonBuilder
import com.quty.erp.BuildConfig
import com.quty.erp.data.local.TokenManager
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit API Client Configuration
 * Handles:
 * - JWT token injection (Bearer auth)
 * - Request/response logging (debug only)
 * - Connection timeout & retry logic
 * - Error handling
 */
class ApiClient(private val tokenManager: TokenManager) {

    private val httpClient: OkHttpClient
        get() {
            val builder = OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)

            // ✅ JWT Token Interceptor - Add Authorization header
            builder.addInterceptor { chain ->
                val originalRequest = chain.request()
                val token = tokenManager.getToken()
                
                val newRequest = originalRequest.newBuilder()
                    .apply {
                        if (token != null) {
                            addHeader("Authorization", "Bearer $token")
                        }
                    }
                    .addHeader("Content-Type", "application/json")
                    .build()

                chain.proceed(newRequest)
            }

            // ✅ Logging Interceptor (debug only)
            if (BuildConfig.DEBUG) {
                val logging = HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                }
                builder.addInterceptor(logging)
            }

            return@get builder.build()
        }

    private val gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        .create()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    inline fun <reified T> createService(): T = retrofit.create(T::class.java)
}

// ============================================================================
// API SERVICE INTERFACES
// ============================================================================

import retrofit2.Response
import retrofit2.http.*
import java.time.LocalDate

/**
 * Production API - Daily Input Endpoints
 * BASE: /production
 */
interface ProductionApi {

    /**
     * POST /production/spk/{spk_id}/daily-input
     * Production staff record daily production
     */
    @POST("/production/spk/{spk_id}/daily-input")
    suspend fun recordDailyInput(
        @Path("spk_id") spkId: Int,
        @Body request: RecordDailyInputRequest
    ): Response<ApiResponse<DailyInputResponse>>

    /**
     * GET /production/spk/{spk_id}/progress
     * Get SPK progress tracking
     */
    @GET("/production/spk/{spk_id}/progress")
    suspend fun getSPKProgress(
        @Path("spk_id") spkId: Int
    ): Response<ApiResponse<SPKProgressResponse>>

    /**
     * GET /production/my-spks
     * Get all SPKs assigned to production staff
     */
    @GET("/production/my-spks")
    suspend fun getMySpks(
        @Query("status") status: String? = null
    ): Response<ApiResponse<List<SPKListItemResponse>>>
}

/**
 * FinishGood API - Barcode Scanning & Verification
 * BASE: /warehouse/finishgood
 */
interface FinishGoodApi {

    /**
     * GET /warehouse/finishgood/pending-transfers
     * Get pending cartons for counting
     */
    @GET("/warehouse/finishgood/pending-transfers")
    suspend fun getPendingTransfers(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): Response<ApiResponse<List<PendingTransferResponse>>>

    /**
     * POST /warehouse/finishgood/verify
     * Verify carton barcode & count
     */
    @POST("/warehouse/finishgood/verify")
    suspend fun verifyCarton(
        @Body request: VerifyCartonRequest
    ): Response<ApiResponse<VerifyCartonResponse>>

    /**
     * POST /warehouse/finishgood/confirm
     * Confirm final count for carton
     */
    @POST("/warehouse/finishgood/confirm")
    suspend fun confirmCarton(
        @Body request: ConfirmCartonRequest
    ): Response<ApiResponse<ConfirmCartonResponse>>
}

/**
 * Authentication API
 * BASE: /auth
 */
interface AuthApi {

    /**
     * POST /auth/login
     * Login with PIN or RFID
     */
    @POST("/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<ApiResponse<LoginResponse>>

    /**
     * POST /auth/refresh
     * Refresh JWT token
     */
    @POST("/auth/refresh")
    suspend fun refreshToken(
        @Body request: RefreshTokenRequest
    ): Response<ApiResponse<LoginResponse>>

    /**
     * POST /auth/logout
     * Logout
     */
    @POST("/auth/logout")
    suspend fun logout(): Response<ApiResponse<Unit>>
}

// ============================================================================
// REQUEST/RESPONSE MODELS
// ============================================================================

// ✅ Production API Models
data class RecordDailyInputRequest(
    val production_date: String,  // "2026-01-26"
    val input_qty: Int,
    val notes: String? = null,
    val status: String = "CONFIRMED"
)

data class DailyInputResponse(
    val spk_id: Int,
    val input_qty: Int,
    val cumulative_qty: Int,
    val target_qty: Int,
    val completion_pct: Float,
    val remaining_qty: Int,
    val status: String,
    val message: String
)

data class SPKProgressResponse(
    val spk_id: Int,
    val spk_number: String,
    val product: String,
    val target_qty: Int,
    val actual_qty: Int,
    val completion_pct: Float,
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
    val est_days_remaining: Int
)

data class SPKListItemResponse(
    val spk_id: Int,
    val spk_number: String,
    val product: String,
    val target_qty: Int,
    val actual_qty: Int,
    val completion_pct: Float,
    val status: String,
    val created_date: String
)

// ✅ FinishGood API Models
data class PendingTransferResponse(
    val transfer_id: Int,
    val carton_id: String,
    val article: String,        // IKEA article code
    val article_name: String,
    val qty: Int,
    val status: String,
    val barcode: String
)

data class VerifyCartonRequest(
    val carton_id: String,
    val scanned_barcode: String,
    val manual_count: Int? = null
)

data class VerifyCartonResponse(
    val carton_id: String,
    val article: String,
    val system_qty: Int,
    val manual_count: Int,
    val match: Boolean,
    val message: String
)

data class ConfirmCartonRequest(
    val transfer_id: Int,
    val carton_id: String,
    val final_count: Int,
    val notes: String? = null
)

data class ConfirmCartonResponse(
    val carton_id: String,
    val status: String,
    val message: String
)

// ✅ Auth API Models
data class LoginRequest(
    val pin: String? = null,
    val rfid_card: String? = null
)

data class LoginResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val user: UserInfo
)

data class UserInfo(
    val id: Int,
    val username: String,
    val email: String,
    val role: String,
    val department: String
)

data class RefreshTokenRequest(
    val refresh_token: String
)

// ✅ Generic API Response Wrapper
data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val message: String? = null,
    val timestamp: String? = null,
    val errors: Map<String, String>? = null
)
