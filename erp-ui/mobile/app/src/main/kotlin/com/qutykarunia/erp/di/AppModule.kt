package com.qutykarunia.erp.di

import android.content.Context
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import com.qutykarunia.erp.data.api.*
import javax.inject.Singleton

/**
 * Hilt Dependency Injection Module
 * 
 * Provides:
 * - API client instances (Retrofit)
 * - Database instances (Room)
 * - Repository implementations
 * - Use case factories
 */
@Module
@InstallIn(SingletonComponent::class)
object ApiModule {
    
    @Provides
    @Singleton
    fun provideProductionApi(
        @ApplicationContext context: Context
    ): ProductionApi {
        return ApiClient.getProductionApi(context)
    }
    
    @Provides
    @Singleton
    fun providePPICApi(
        @ApplicationContext context: Context
    ): PPICApi {
        return ApiClient.getPPICApi(context)
    }
    
    @Provides
    @Singleton
    fun provideFinishGoodApi(
        @ApplicationContext context: Context
    ): FinishGoodApi {
        return ApiClient.getFinishGoodApi(context)
    }
}

/**
 * Room Database Module (for future use)
 * 
 * When implementing Room database:
 * 
 * @Module
 * @InstallIn(SingletonComponent::class)
 * object DatabaseModule {
 *     
 *     @Provides
 *     @Singleton
 *     fun provideAppDatabase(
 *         @ApplicationContext context: Context
 *     ): AppDatabase {
 *         return Room.databaseBuilder(
 *             context,
 *             AppDatabase::class.java,
 *             "erp_app_database"
 *         )
 *         .fallbackToDestructiveMigration()
 *         .build()
 *     }
 *     
 *     @Provides
 *     @Singleton
 *     fun provideOfflineSyncDao(
 *         database: AppDatabase
 *     ): OfflineSyncDao {
 *         return database.offlineSyncDao()
 *     }
 * }
 */
