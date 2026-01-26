package com.qutykarunia.erp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import dagger.hilt.android.AndroidEntryPoint
import com.qutykarunia.erp.ui.screens.LoginScreen
import com.qutykarunia.erp.ui.screens.DashboardScreen
import com.qutykarunia.erp.ui.screens.DailyProductionInputScreen
import com.qutykarunia.erp.ui.screens.FinishGoodBarcodeScreen
import com.qutykarunia.erp.ui.theme.ERPTheme

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ERPTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ERPNavigation()
                }
            }
        }
    }
}

@Composable
fun ERPNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "login"
    ) {
        composable("login") {
            LoginScreen(navController = navController)
        }

        composable("dashboard") {
            DashboardScreen(navController = navController)
        }

        composable("daily_production") {
            DailyProductionInputScreen(navController = navController)
        }

        composable("finish_good_barcode") {
            FinishGoodBarcodeScreen(navController = navController)
        }
    }
}
