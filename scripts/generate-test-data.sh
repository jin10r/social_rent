#!/bin/bash

# Script to generate all test data
# Usage: ./scripts/generate-test-data.sh

set -e

echo "🔄 Generating test data for Social Rent App..."

cd backend

echo "👥 Generating 100 test users..."
python generate_users.py

echo "🏠 Generating 1000 test listings..."
python generate_listings.py

cd ..

echo "✅ Test data generation completed!"
echo "📊 Database now contains:"
echo "   - 100 test users with profiles"
echo "   - 1000 apartment listings in Moscow"
echo ""
echo "🚀 Ready for testing!"