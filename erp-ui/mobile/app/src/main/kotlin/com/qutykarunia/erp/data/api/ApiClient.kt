package com.qutykarunia.erp.data.api

import android.content.Context
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.concurrent.TimeUnit

/**
 * Retrofit API Client Setup
 * Handles JWT authentication, logging, and timeouts
 */
object ApiClient {
    
    private const val BASE_URL = "http://localhost:8000"
    private const val CONNECT_TIMEOUT = 30L
    private const val READ_TIMEOUT = 30L
    private const val WRITE_TIMEOUT = 30L
    
    private var retrofit: Retrofit? = null
    
    fun getRetrofit(context: Context): Retrofit {
        if (retrofit == null) {
            retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(getOkHttpClient(context))
                .addConverterFactory(GsonConverterFactory.create(getGson()))
                .build()
        }
        return retrofit!!
    }
    
    private fun getOkHttpClient(context: Context): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(JwtInterceptor(context))
            .addInterceptor(getLoggingInterceptor())
            .connectTimeout(CONNECT_TIMEOUT, TimeUnit.SECONDS)
            .readTimeout(READ_TIMEOUT, TimeUnit.SECONDS)
            .writeTimeout(WRITE_TIMEOUT, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }
    
    private fun getLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }
    
    private fun getGson(): Gson {
        return GsonBuilder()
            .registerTypeAdapter(LocalDate::class.java, LocalDateTypeAdapter())
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
            .create()
    }
    
    fun getProductionApi(context: Context): ProductionApi {
        return getRetrofit(context).create(ProductionApi::class.java)
    }
    
    fun getPPICApi(context: Context): PPICApi {
        return getRetrofit(context).create(PPICApi::class.java)
    }
    
    fun getFinishGoodApi(context: Context): FinishGoodApi {
        return getRetrofit(context).create(FinishGoodApi::class.java)
    }
}

/**
 * JWT Interceptor - Adds authorization header to all requests
 */
class JwtInterceptor(private val context: Context) : okhttp3.Interceptor {
    
    override fun intercept(chain: okhttp3.Interceptor.Chain): okhttp3.Response {
        val request = chain.request().newBuilder()
        
        // Get JWT token from secure storage
        val token = TokenManager.getToken(context)
        
        if (!token.isNullOrEmpty()) {
            request.addHeader("Authorization", "Bearer $token")
        }
        
        request.addHeader("Content-Type", "application/json")
        request.addHeader("Accept", "application/json")
        
        return chain.proceed(request.build())
    }
}

/**
 * JWT Token Manager - Handles secure token storage and refresh
 */
object TokenManager {
    private const val PREF_NAME = "erp_auth"
    private const val TOKEN_KEY = "jwt_token"
    private const val REFRESH_TOKEN_KEY = "refresh_token"
    private const val TOKEN_EXPIRE_TIME = "token_expire"
    
    fun saveToken(context: Context, token: String, expiresIn: Long = 86400) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().apply {
            putString(TOKEN_KEY, token)
            putLong(TOKEN_EXPIRE_TIME, System.currentTimeMillis() + (expiresIn * 1000))
            apply()
        }
    }
    
    fun saveRefreshToken(context: Context, refreshToken: String) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(REFRESH_TOKEN_KEY, refreshToken).apply()
    }
    
    fun getToken(context: Context): String? {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return prefs.getString(TOKEN_KEY, null)
    }
    
    fun getRefreshToken(context: Context): String? {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        return prefs.getString(REFRESH_TOKEN_KEY, null)
    }
    
    fun clearTokens(context: Context) {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        prefs.edit().clear().apply()
    }
    
    fun isTokenExpired(context: Context): Boolean {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        val expireTime = prefs.getLong(TOKEN_EXPIRE_TIME, 0)
        return System.currentTimeMillis() > expireTime
    }
}

/**
 * LocalDate Type Adapter for Gson
 */
class LocalDateTypeAdapter : com.google.gson.JsonSerializer<LocalDate>,
    com.google.gson.JsonDeserializer<LocalDate> {
    
    private val formatter = DateTimeFormatter.ISO_DATE
    
    override fun serialize(
        src: LocalDate?,
        typeOfSrc: java.lang.reflect.Type?,
        context: com.google.gson.JsonSerializationContext?
    ): com.google.gson.JsonElement {
        return com.google.gson.JsonPrimitive(src?.format(formatter))
    }
    
    override fun deserialize(
        json: com.google.gson.JsonElement?,
        typeOfT: java.lang.reflect.Type?,
        context: com.google.gson.JsonDeserializationContext?
    ): LocalDate {
        return LocalDate.parse(json?.asString, formatter)
    }
}
