package middleware

import (
	"errors"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/stev97uce/room-service/pkg/config"
)

type Claims struct {
	UserID     int    `json:"user_id"`
	Email      string `json:"email"`
	Role       string `json:"role"`
	IsVerified bool   `json:"is_verified"`
	jwt.RegisteredClaims
}

// AuthMiddleware validates JWT token
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "authorization header required"})
			c.Abort()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid authorization format"})
			c.Abort()
			return
		}

		token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, errors.New("invalid signing method")
			}
			return []byte(config.AppConfig.JWTSecretKey), nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid or expired token"})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(*Claims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token claims"})
			c.Abort()
			return
		}

		// Store claims in context
		c.Set("user_id", claims.UserID)
		c.Set("email", claims.Email)
		c.Set("role", claims.Role)
		c.Set("is_verified", claims.IsVerified)

		c.Next()
	}
}

// RequireRole checks if user has required role
func RequireRole(roles ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get("role")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "role not found in token"})
			c.Abort()
			return
		}

		userRole := role.(string)
		hasRole := false
		for _, r := range roles {
			if r == userRole {
				hasRole = true
				break
			}
		}

		if !hasRole {
			c.JSON(http.StatusForbidden, gin.H{"error": "insufficient permissions"})
			c.Abort()
			return
		}

		c.Next()
	}
}

// GetUserID extracts user ID from context
func GetUserID(c *gin.Context) (int, error) {
	userID, exists := c.Get("user_id")
	if !exists {
		return 0, errors.New("user_id not found in context")
	}
	return userID.(int), nil
}

// GetUserRole extracts role from context
func GetUserRole(c *gin.Context) (string, error) {
	role, exists := c.Get("role")
	if !exists {
		return "", errors.New("role not found in context")
	}
	return role.(string), nil
}
