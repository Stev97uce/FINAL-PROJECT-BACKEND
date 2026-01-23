package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestLogger(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	c.Request, _ = http.NewRequest("GET", "/test", nil)

	handler := Logger()

	// Execute middleware
	handler(c)

	// Middleware should not block the request
	if w.Code != 0 && w.Code != http.StatusOK {
		t.Errorf("Expected status code 0 or 200, got %d", w.Code)
	}
}

func TestAuthMiddleware_NoToken(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, router := gin.CreateTestContext(w)

	router.Use(AuthMiddleware())
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	c.Request, _ = http.NewRequest("GET", "/protected", nil)
	router.ServeHTTP(w, c.Request)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status code %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_InvalidToken(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, router := gin.CreateTestContext(w)

	router.Use(AuthMiddleware())
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	c.Request, _ = http.NewRequest("GET", "/protected", nil)
	c.Request.Header.Set("Authorization", "Bearer invalid_token")
	router.ServeHTTP(w, c.Request)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status code %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestAuthMiddleware_MalformedToken(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, router := gin.CreateTestContext(w)

	router.Use(AuthMiddleware())
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	c.Request, _ = http.NewRequest("GET", "/protected", nil)
	c.Request.Header.Set("Authorization", "InvalidFormat")
	router.ServeHTTP(w, c.Request)

	if w.Code != http.StatusUnauthorized {
		t.Errorf("Expected status code %d, got %d", http.StatusUnauthorized, w.Code)
	}
}

func TestRequireRole_NoUser(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, router := gin.CreateTestContext(w)

	router.Use(RequireRole("admin"))
	router.GET("/admin", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	c.Request, _ = http.NewRequest("GET", "/admin", nil)
	router.ServeHTTP(w, c.Request)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status code %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestRequireRole_WrongRole(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, router := gin.CreateTestContext(w)

	// Set user with wrong role
	c.Set("user", map[string]interface{}{
		"user_id": 1,
		"rol":     "estudiante",
	})

	router.Use(RequireRole("admin"))
	router.GET("/admin", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	c.Request, _ = http.NewRequest("GET", "/admin", nil)
	router.ServeHTTP(w, c.Request)

	if w.Code != http.StatusForbidden {
		t.Errorf("Expected status code %d, got %d", http.StatusForbidden, w.Code)
	}
}

func TestRequireRole_CorrectRole(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	// Set role as the auth middleware would
	c.Set("role", "admin")

	// Create middleware and execute
	middleware := RequireRole("admin")
	middleware(c)

	// Check if middleware passed (didn't abort)
	if c.IsAborted() {
		t.Error("Middleware should not abort for correct role")
	}
}

func TestRequireRole_MultipleAllowedRoles(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)

	// Set role as coordinador
	c.Set("role", "coordinador")

	// Create middleware and execute
	middleware := RequireRole("admin", "coordinador")
	middleware(c)

	// Check if middleware passed (didn't abort)
	if c.IsAborted() {
		t.Error("Middleware should not abort for allowed role")
	}
}
