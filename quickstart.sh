#!/bin/bash
# Quick start script for local development

set -e

echo "=========================================="
echo "OPD Claim Adjudication MVP - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    
    # Check if docker-compose is available
    if command -v docker-compose &> /dev/null; then
        echo "✓ Docker Compose found"
        echo ""
        echo "Starting services with Docker Compose..."
        echo ""
        
        # Build images
        echo "Building Docker images..."
        docker-compose build
        
        # Start services
        echo ""
        echo "Starting services..."
        docker-compose up -d
        
        echo ""
        echo "Waiting for services to start..."
        sleep 10
        
        # Check health
        echo ""
        echo "Checking service health..."
        
        # Check API
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✓ API (http://localhost:8000) is running"
        else
            echo "✗ API failed to start. Check logs: docker-compose logs api"
        fi
        
        # Check Web
        if curl -s http://localhost:3000 > /dev/null; then
            echo "✓ Web (http://localhost:3000) is running"
        else
            echo "⟳ Web starting... (takes 30-60 seconds)"
        fi
        
        echo ""
        echo "=========================================="
        echo "Services Ready!"
        echo "=========================================="
        echo ""
        echo "Frontend: http://localhost:3000"
        echo "API: http://localhost:8000"
        echo "API Health: http://localhost:8000/health"
        echo "Database: localhost:5432 (opd_user/opd_password)"
        echo ""
        echo "Next steps:"
        echo "  1. Open http://localhost:3000 in your browser"
        echo "  2. Run tests: docker-compose exec api pytest tests/ -v"
        echo "  3. View logs: docker-compose logs -f"
        echo "  4. Stop services: docker-compose down"
        echo ""
    else
        echo "✗ Docker Compose not found. Please install it."
        exit 1
    fi
else
    echo "✗ Docker not found. Setting up local development..."
    echo ""
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON=python3
        echo "✓ Python 3 found"
    elif command -v python &> /dev/null; then
        PYTHON=python
        echo "✓ Python found"
    else
        echo "✗ Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Node
    if command -v node &> /dev/null; then
        echo "✓ Node.js found"
    else
        echo "✗ Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    echo ""
    echo "Setting up backend..."
    cd apps/api
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        $PYTHON -m venv venv
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
    
    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt > /dev/null
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << EOF
FLASK_ENV=development
FLASK_APP=wsgi.py
DATABASE_URL=postgresql://localhost/opd_claim_dev
API_KEY=local-dev
EOF
    fi
    
    echo "✓ Backend setup complete"
    echo ""
    echo "Setting up frontend..."
    cd ../../apps/web
    
    if [ ! -d "node_modules" ]; then
        echo "Installing Node dependencies..."
        npm install > /dev/null
    fi
    
    echo "✓ Frontend setup complete"
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "To start development servers:"
    echo ""
    echo "Terminal 1 - Backend:"
    echo "  cd apps/api"
    echo "  source venv/bin/activate  # or venv/Scripts/activate on Windows"
    echo "  python wsgi.py"
    echo ""
    echo "Terminal 2 - Frontend:"
    echo "  cd apps/web"
    echo "  npm run dev"
    echo ""
    echo "Then open http://localhost:3000 in your browser"
    echo ""
fi
