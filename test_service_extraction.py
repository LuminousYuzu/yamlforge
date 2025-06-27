#!/usr/bin/env python3
"""
Test script to demonstrate the fuzzy matching service extraction functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yaml_parser.service_extractor import SpringBootServiceExtractor

def test_service_extraction():
    """Test the service extraction with the provided YAML example"""
    
    # Simplified YAML data for testing
    yaml_data = {
        "spring": {
            "application": {
                "name": "test-service",
                "version": "1.0.0"
            },
            "profiles": {
                "active": "dev"
            },
            "datasource": {
                "primary": {
                    "url": "jdbc:postgresql://localhost:5432/testdb",
                    "username": "${DB_USERNAME:postgres}",
                    "password": "${DB_PASSWORD:password}",
                    "driver-class-name": "org.postgresql.Driver"
                },
                "secondary": {
                    "url": "jdbc:mysql://localhost:3306/testdb_secondary",
                    "username": "${MYSQL_USERNAME:root}",
                    "password": "${MYSQL_PASSWORD:password}",
                    "driver-class-name": "com.mysql.cj.jdbc.Driver"
                }
            },
            "redis": {
                "host": "${REDIS_HOST:localhost}",
                "port": "${REDIS_PORT:6379}",
                "password": "${REDIS_PASSWORD:}",
                "database": 0
            },
            "rabbitmq": {
                "host": "${RABBITMQ_HOST:localhost}",
                "port": "${RABBITMQ_PORT:5672}",
                "username": "${RABBITMQ_USERNAME:guest}",
                "password": "${RABBITMQ_PASSWORD:guest}"
            },
            "kafka": {
                "bootstrap-servers": "${KAFKA_BOOTSTRAP_SERVERS:localhost:9092}",
                "consumer": {
                    "group-id": "test-service-group"
                }
            }
        },
        "server": {
            "port": "${SERVER_PORT:8080}",
            "servlet": {
                "context-path": "/api/v1"
            }
        },
        "app": {
            "external-services": {
                "payment-service": {
                    "url": "${PAYMENT_SERVICE_URL:http://localhost:8081}",
                    "timeout": "5000ms",
                    "retry-attempts": 3
                },
                "notification-service": {
                    "url": "${NOTIFICATION_SERVICE_URL:http://localhost:8082}",
                    "timeout": "3000ms",
                    "retry-attempts": 2
                }
            }
        }
    }
    
    # Initialize the service extractor
    extractor = SpringBootServiceExtractor()
    
    # Extract service information
    print("🔍 Extracting service information using fuzzy matching...")
    print("=" * 60)
    
    service_info = extractor.extract_service_info(yaml_data)
    
    # Display results
    print("\n📋 EXTRACTED SERVICE INFORMATION:")
    print("=" * 60)
    
    # Service Name
    if service_info.get('service_name'):
        print(f"🏷️  Service Name: {service_info['service_name']['value']}")
        print(f"   Confidence: {service_info['service_name']['confidence']}%")
        print(f"   Matched Field: {service_info['service_name']['matched_field']}")
    else:
        print("❌ Service Name: Not found")
    
    print()
    
    # Port
    if service_info.get('port'):
        print(f"🔌 Port: {service_info['port']['value']}")
        print(f"   Confidence: {service_info['port']['confidence']}%")
        print(f"   Matched Field: {service_info['port']['matched_field']}")
    else:
        print("❌ Port: Not found")
    
    print()
    
    # Protocol
    if service_info.get('protocol'):
        print(f"🌐 Protocol: {service_info['protocol']['value']}")
        print(f"   Confidence: {service_info['protocol']['confidence']}%")
        print(f"   Reason: {service_info['protocol']['reason']}")
    else:
        print("❌ Protocol: Not found")
    
    print()
    
    # Dependent Services
    print("🔗 Dependent Services:")
    if service_info.get('dependent_services'):
        for service in service_info['dependent_services']:
            print(f"   • {service['name']}")
            print(f"     URL: {service['url']}")
            print(f"     Timeout: {service['timeout']}")
            print(f"     Retry Attempts: {service['retry_attempts']}")
    else:
        print("   None found")
    
    print()
    
    # Dependent Infrastructure
    print("🏗️  Dependent Infrastructure:")
    if service_info.get('dependent_infrastructure'):
        for infra in service_info['dependent_infrastructure']:
            print(f"   • {infra['type'].upper()}")
            print(f"     Configuration Key: {infra['configuration_key']}")
            if infra['details']:
                for key, value in infra['details'].items():
                    if value:
                        print(f"     {key}: {value}")
    else:
        print("   None found")
    
    print()
    
    # Additional Data
    print("📊 Additional Data:")
    if service_info.get('additional_data'):
        additional = service_info['additional_data']
        if additional.get('version'):
            print(f"   Version: {additional['version']}")
        if additional.get('profiles'):
            print(f"   Profiles: {', '.join(additional['profiles'])}")
    else:
        print("   None found")
    
    print("\n" + "=" * 60)
    print("✅ Service extraction completed successfully!")
    print("\nThis demonstrates how the fuzzy matching algorithm intelligently extracts:")
    print("• Service name from 'spring.application.name'")
    print("• Port from 'server.port' with environment variable handling")
    print("• Protocol detection (HTTP/HTTPS)")
    print("• Dependent services from 'app.external-services'")
    print("• Infrastructure dependencies (PostgreSQL, MySQL, Redis, RabbitMQ, Kafka)")
    print("• Additional metadata (version, profiles, etc.)")

if __name__ == "__main__":
    test_service_extraction() 