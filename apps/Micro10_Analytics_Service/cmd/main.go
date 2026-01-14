package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/stev97uce/analytics-service/internal/handlers"
	"github.com/stev97uce/analytics-service/internal/middleware"
	"github.com/stev97uce/analytics-service/internal/repository"
	"github.com/stev97uce/analytics-service/internal/services"
	"github.com/stev97uce/analytics-service/pkg/config"
	"github.com/stev97uce/analytics-service/pkg/database"
)

func main() {
	if err := config.LoadConfig(); err != nil {
		log.Fatal("Failed to load configuration:", err)
	}

	if err := database.InitMongoDB(); err != nil {
		log.Fatal("Failed to initialize MongoDB:", err)
	}

	if err := database.InitRedis(); err != nil {
		log.Fatal("Failed to initialize Redis:", err)
	}

	metricRepo := repository.NewMetricRepository()
	dashboardRepo := repository.NewDashboardRepository()

	metricService := services.NewMetricService(metricRepo)
	dashboardService := services.NewDashboardService(dashboardRepo)

	metricHandler := handlers.NewMetricHandler(metricService)
	dashboardHandler := handlers.NewDashboardHandler(dashboardService)

	if !config.AppConfig.Debug {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(middleware.Logger())

	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000", "http://localhost:5173"},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	router.GET("/health", func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()

		status := "healthy"
		mongoStatus := "connected"
		redisStatus := "connected"

		if err := database.HealthCheck(ctx); err != nil {
			status = "unhealthy"
			if database.MongoDB == nil {
				mongoStatus = "disconnected"
			}
			if database.RedisClient == nil {
				redisStatus = "disconnected"
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"status":   status,
			"service":  config.AppConfig.AppName,
			"version":  config.AppConfig.AppVersion,
			"mongodb":  mongoStatus,
			"redis":    redisStatus,
		})
	})

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"service": config.AppConfig.AppName,
			"version": config.AppConfig.AppVersion,
			"status":  "running",
		})
	})

	v1 := router.Group("/api/v1")

	metrics := v1.Group("/metrics")
	metrics.Use(middleware.AuthMiddleware())
	{
		metrics.POST("/", middleware.RequireRole("admin", "coordinador"), metricHandler.CreateMetric)
		metrics.GET("/", metricHandler.GetMetrics)
		metrics.GET("/latest/:type", metricHandler.GetLatestMetric)
		metrics.GET("/summary", metricHandler.GetDashboardSummary)
	}

	dashboards := v1.Group("/dashboards")
	dashboards.Use(middleware.AuthMiddleware())
	{
		dashboards.POST("/", dashboardHandler.CreateDashboard)
		dashboards.GET("/", dashboardHandler.ListDashboards)
		dashboards.GET("/:id", dashboardHandler.GetDashboard)
		dashboards.PUT("/:id", dashboardHandler.UpdateDashboard)
		dashboards.DELETE("/:id", middleware.RequireRole("admin", "coordinador"), dashboardHandler.DeleteDashboard)
	}

	srv := &http.Server{
		Addr:    ":" + config.AppConfig.Port,
		Handler: router,
	}

	go func() {
		log.Printf("Starting %s v%s on port %s", config.AppConfig.AppName, config.AppConfig.AppVersion, config.AppConfig.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal("Failed to start server:", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	database.CloseConnections()
	log.Println("Server exited")
}
